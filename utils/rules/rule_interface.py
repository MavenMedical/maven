ENCOUNTERDX = 'encounter_dx'
PROBLEMLISTDX = 'problemlist_dx'
EXISTS = 'exists'
SNOMED = 'snomed'
RULENAME = 'rulename'
SHORTDESC = 'shortdescription'
HTML = 'HTML'

import json
import asyncio
from collections import defaultdict

class RuleInterface:

    @asyncio.coroutine
    def list_rules(self):
        raise NotImplementedError

    @asyncio.coroutine
    def put_rule(self, rule_name, short_desc, rule_html, rule_json, old_rule_id=None):
        raise NotImplementedError

    @asyncio.coroutine
    def find_candidate_matches(self, current_composition):
        raise NotImplementedError

    @asyncio.coroutine
    def get_rule(self, rule_id):
        raise NotImplementedError
        
class StaticRuleInterface(RuleInterface):
    def __init__(self):
        self.rules = {
            1:{ENCOUNTERDX:1234},
            2:{ENCOUNTERDX:1234,PROBLEMLISTDX:5678},
            3:{ENCOUNTERDX:2345},
            }

        self.old_rules=defaultdict(lambda:[])

        self.rule_desc = {
            1:{RULENAME:'rule1', SHORTDESC:'this is the first rule', HTML:'<div>This is the first rule</div>',},
            2:{RULENAME:'rule2', SHORTDESC:'this is the second rule', HTML:'<div>This is the second rule</div>',},
            3:{RULENAME:'rule3', SHORTDESC:'this is the third rule', HTML:'<div>This is the third rule</div>',},
           }

        self.next_id=4

    @asyncio.coroutine
    def list_rules(self):
        return {id:self.rule_desc[id][RULENAME] for id in self.rule_desc}

    @asyncio.coroutine
    def put_rule(self, rule_name, short_desc, rule_html, rule_json, old_rule_id=None):
        if old_rule_id and old_rule_id in self.rules:
            self.old_rules[old_rule_id].append(self.rules[old_rule_id])
            id = old_rule_id
        else:
            id = self.next_id
            self.next_id += 1
        
        self.rule_desc[id]={RULENAME:rule_name, SHORTDESC:short_desc, HTML:rule_html}
        self.rules[id]=json.loads(rule_json)
        return id

    @asyncio.coroutine
    def find_candidate_matches(self, current_composition):
        return {id:json.dumps(self.rules[id]) for id in self.rules}

    @asyncio.coroutine
    def get_rule(self, rule_id):
        # throws KeyError is the rule doesn't exist
        return (self.rule_desc[rule_id], self.rules[rule_id])
