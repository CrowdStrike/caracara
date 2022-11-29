"""Caracara Indicator of Attack (IOA) API module."""
from functools import partial
from time import monotonic
from typing import Dict, List

from falconpy import OAuth2, CustomIOA

from caracara.common.batching import batch_get_data
from caracara.common.constants import DEFAULT_COMMENT
from caracara.common.pagination import all_pages_numbered_offset_parallel
from caracara.filters import FalconFilter
from caracara.filters.decorators import filter_string
from caracara.common.module import FalconApiModule
from caracara.modules.custom_ioa.rules import CustomIoaRule, IoaRuleGroup, RuleType


# instrument falconpy to raise exceptions
def instr(func) -> dict:
    """Instrument FalconPy functions with basic error handling.

    This is an internal function, and therefore developers should not expect this function to
    remain consistent.
    """
    def handle_errors(*args, **kwargs):
        response = func(*args, **kwargs)
        errors = response["body"].get("errors", [])
        if len(errors) == 0:
            return response
        raise Exception(errors)
    return handle_errors


class CustomIoaApiModule(FalconApiModule):
    """Caracara Custom Indicator of Attack (IOA) API module."""

    name = "CrowdStrike Custom IOA Module"
    help = "Interact with Custom IOA Rules and IOA Rule Groups within your Falcon tenant."

    # Don't access directly, always use _get_rule_types_cached
    _rule_type_cache: Dict[str, RuleType]
    _rule_type_cache_time: int = None
    _rule_type_cache_ttl: int = 10 * 60  # 10 minute default cache TTL

    def __init__(self, api_authentication: OAuth2):
        """Create an Custom IOA API object and configure it with a FalconPy OAuth2 object."""
        super().__init__(api_authentication)
        self.custom_ioa_api = CustomIOA(auth_object=api_authentication)

    def _get_rule_types_cached(self, force_update: bool = False) -> Dict[str, RuleType]:
        cur_time = monotonic()
        # If cache has expired
        if self._rule_type_cache_time is None:
            force_update = True
        if force_update or cur_time >= self._rule_type_cache_time + self._rule_type_cache_ttl:
            self._rule_type_cache = self.describe_rule_types()
            self._rule_type_cache_time = cur_time
        return self._rule_type_cache

    def create_rule_group(
        self, group: IoaRuleGroup, comment: str = DEFAULT_COMMENT
    ) -> IoaRuleGroup:
        """Create a new rule group from a manually constructed `IoaRuleGroup`.

        This creates the provided rule group (provided it does not already exist), and also creates
        all the rules within the rule group (added with `IoaRuleGroup.add_rule`).

        Arguments
        ---------
        `group`: `IoaRuleGroup`
            The group to create in the cloud (note this group must not already exist in the cloud,
            i.e. `group.exists_in_cloud() == False`)
        `comment`: `str`
            The comment to associate with this action in the audit log

        Returns
        -------
        `IoaRuleGroup`: The object representing the newly created rule group in the cloud
        """
        if group.exists_in_cloud():
            raise Exception("This group already exists in the cloud!")

        group.validation()

        # Create the group
        group_create = group.dump_create(comment=comment)
        response = instr(self.custom_ioa_api.create_rule_group)(body=group_create)
        new_group = IoaRuleGroup.from_data_dict(
            data_dict=response["body"]["resources"][0], rule_type_map=self._get_rule_types_cached())
        new_group.rules = group.rules
        for rule in new_group.rules:
            rule.group = new_group

        # Update the rules
        new_group = self._create_update_delete_rules(new_group, comment=comment)

        return new_group

    def update_rule_group(
        self, group: IoaRuleGroup, comment: str = DEFAULT_COMMENT
    ) -> IoaRuleGroup:
        """Update a group that already exists in the cloud.

        This will also sync the state of the rules with the cloud, i.e. creating rules that don't
        yet exist, updating existing rules that have changes, and deleting any locally removed
        rules.

        Arguments
        ---------
        `group`: `IoaRuleGroup`
            The group to update.
        `comment`: `str`
            The comment to associate with this action in the audit log

        Returns
        -------
        `IoaRuleGroup`: The updated group.
        """
        if not group.exists_in_cloud():
            raise Exception("This group does not exist in the cloud!")

        group.validation()

        # Update the group
        group_update = group.dump_update(comment=comment)
        response = instr(self.custom_ioa_api.update_rule_group)(body=group_update)
        new_group = IoaRuleGroup.from_data_dict(
            data_dict=response["body"]["resources"][0], rule_type_map=self._get_rule_types_cached())

        # Retain staged rules (as these aren't in the cloud yet, but will be soon)
        new_group.rules = group.rules
        new_group.rules_to_delete = group.rules_to_delete

        # Update the rules
        new_group = self._create_update_delete_rules(new_group, comment=comment)

        return new_group

    def delete_rule_groups(
        self, rule_groups: List[IoaRuleGroup or str], comment: str = DEFAULT_COMMENT
    ):
        """Delete a list of rule groups in the cloud.

        Arguments
        ---------
        `rule_groups`: `List[IoaRuleGroup or str]`
            The list of rule groups as objects or just IDs
        `comment`: `str`
            The comment to associated with this deletion.
        """
        if len(rule_groups) == 0:  # Do nothing if no rule groups to delete
            return

        ids_to_delete = []
        for rule_group in rule_groups:
            if isinstance(rule_group, IoaRuleGroup):
                ids_to_delete.append(rule_group.id_)
            else:
                ids_to_delete.append(rule_group)
        instr(self.custom_ioa_api.delete_rule_groups)(ids=ids_to_delete, comment=comment)

    def _create_update_delete_rules(self, group: IoaRuleGroup, comment: str) -> IoaRuleGroup:
        existing_rules = []
        to_be_created = []
        for rule in group.rules:
            if rule.exists_in_cloud():
                existing_rules.append(rule)
            else:
                to_be_created.append(rule)

        # Create the new rules
        new_rules = []
        for rule in to_be_created:
            resp = instr(self.custom_ioa_api.create_rule)(
                body=rule.dump_create(comment=comment))
            raw_rule = resp["body"]["resources"][0]
            new_rule = CustomIoaRule.from_data_dict(
                raw_rule, rule_type=self._get_rule_types_cached()[raw_rule["ruletype_id"]])
            new_rule.rulegroup_id = group.id_
            new_rules.append(new_rule)

        # Update the existing rules, if there are any
        if len(existing_rules) > 0:
            response = instr(self.custom_ioa_api.update_rules)(body={
                "comment": comment,
                "rule_updates": [rule.dump_update() for rule in existing_rules],
                "rulegroup_version": group.version + 1,
                "rulegroup_id": group.id_,
            })
            raw_group = response["body"]["resources"][0]

            # Create the object representing the updated group
            rule_types = self._get_rule_types_cached()
            new_group = IoaRuleGroup.from_data_dict(data_dict=raw_group, rule_type_map=rule_types)
        else:
            group.rules = new_rules
            new_group = group

        # Delete rules queued for deletion, if any
        if len(group.rules_to_delete) > 0:
            ids_to_delete = [rule.instance_id for rule in group.rules_to_delete]
            instr(self.custom_ioa_api.delete_rules)(
                rule_group_id=group.id_, ids=ids_to_delete, comment=comment)
            # If successful (i.e. no exceptions raised), clear the deletion queue
            group.rules_to_delete = []
        return new_group

    @filter_string
    def describe_rule_groups_raw(self, filters: str or FalconFilter = None) -> Dict[str, dict]:
        """Return all IOA Rule Groups as raw dicts returned from the API, optionally filtered.

        Arguments
        ---------
        `filters`: `FalconFilter` or `str`, optional
            Filters to apply to IOA rule group search

        Returns
        -------
        `Dict[str, IoaRuleGroup]`:
            Dictionary mapping ID to IOA rule group as a raw dict for all the rule groups that match
            the filter.
        """
        self.logger.info("Describing all Falcon IOA Rule Groups matching filter: %s", repr(filters))
        partial_func = partial(
            instr(self.custom_ioa_api.query_rule_groups_full),
            filter=filters,
        )
        resources = all_pages_numbered_offset_parallel(func=partial_func, logger=self.logger)
        self.logger.debug(resources)
        result = {}
        for rule_group in resources:
            result[rule_group["id"]] = rule_group
        return result

    @filter_string
    def describe_rule_groups(self, filters: str or FalconFilter = None) -> Dict[str, IoaRuleGroup]:
        """Return all IOA Rule Groups, optionally filtered.

        Arguments
        ---------
        `filters`: `FalconFilter` or `str`, optional
            Filters to apply to IOA rule group search

        Returns
        -------
        `Dict[str, IoaRuleGroup]`:
            Dictionary mapping ID to IoaRuleGroup for all the rule groups that match the filter.
        """
        raw_groups = self.describe_rule_groups_raw(filters=filters)
        groups = {}
        rule_types = self._get_rule_types_cached()

        for (group_id, raw_group) in raw_groups.items():
            groups[group_id] = IoaRuleGroup.from_data_dict(
                data_dict=raw_group, rule_type_map=rule_types)
        return groups

    def get_rule_types_raw(self, rule_type_ids: List[str]) -> Dict[str, dict]:
        """Get rule types as raw dicts returned by the API, by ID.

        Arguments
        ---------
        `rule_type_ids`: `List[str]`
            List of rule type IDs

        Returns
        -------
        `Dict[str, dict]`:
            Dictionary mapping ID to its associated rule type as a raw dict returned by the api.
        """
        rule_types = batch_get_data(
            rule_type_ids, instr(self.custom_ioa_api.get_rule_types)
        )

        return rule_types

    def get_rule_types(self, rule_type_ids: List[str]) -> Dict[str, RuleType]:
        """Get rule types by ID.

        Arguments
        ---------
        `rule_type_ids`: `List[str]`
            List of rule type IDs

        Returns
        -------
        `Dict[str, RuleType]`:
            Dictionary mapping ID to its associated rule type.
        """
        rule_types = self.get_rule_types_raw(rule_type_ids=rule_type_ids)
        for i, rule_type in rule_types.items():
            rule_types[i] = RuleType.from_data_dict(rule_type)
        return rule_types

    def get_rule_type_ids(self) -> List[str]:
        """Get all rule type IDs.

        Returns
        -------
        `List[str]` list of rule type IDs
        """
        rule_type_ids = all_pages_numbered_offset_parallel(
            instr(self.custom_ioa_api.query_rule_types), logger=self.logger)
        return rule_type_ids

    def describe_rule_types(self) -> Dict[str, RuleType]:
        """Get all rule types.

        Returns
        -------
        `Dict[str, RuleType]`: Dictionary mapping ID to its associated rule type
        """
        rule_type_ids = self.get_rule_type_ids()
        rule_types = self.get_rule_types(rule_type_ids=rule_type_ids)
        return rule_types
