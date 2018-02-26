from collections import Iterable
from questgen import facts


class KnowledgeBase:
    def __init__(self):
        self._actions = {}

    def create_story(self, events):
        for event in events:
            self._actions[event.uid] = event

    def filter(self, fact_type):
        return (fact for fact in self.facts() if isinstance(fact, fact_type))

    def uids(self):
        return set(self._actions.keys())

    def facts(self):
        return (self._actions[fact_uid] for fact_uid in self.uids())

    def __getitem__(self, fact_uid):
        if fact_uid in self._actions:
            return self._actions[fact_uid]
        raise ValueError(fact_uid)

    def __iadd__(self, fact, expected_fact=False):
        if isinstance(fact, Iterable) and not expected_fact:
            for element in fact:
                self.__iadd__(element, expected_fact=True)
        else:
            self._actions[fact.uid] = fact

        return self

    def __isub__(self, fact, expected_fact=False):
        if isinstance(fact, Iterable) and not expected_fact:
            for element in fact:
                self.__isub__(element, expected_fact=True)
        else:
            del self[fact.uid]

        return self

    def __delitem__(self, fact_uid):
        if fact_uid not in self:
            raise ValueError(fact_uid)
        del self._actions[fact_uid]

    def __contains__(self, fact_uid):
        return fact_uid in self._actions


class Story:

    def __init__(self, knowledge_base):
        self.knowledge_base = knowledge_base

    def _has_jumps(self, fact):
        return bool([jump for jump in self.knowledge_base.filter(Jump) if jump.state_from == fact.uid])

    def is_processed(self, pointer):
        state = self.current_state(pointer)
        if isinstance(state, Finish):
            return True

        return False

    def current_state(self, pointer):
        if pointer.state is None:
            return None
        return self.knowledge_base[pointer.state]

    def get_start_state(self):
        jump_ends = set((jump.state_to for jump in self.knowledge_base.filter(Jump)))
        return next((start for start in self.knowledge_base.filter(Start) if start.uid not in jump_ends))

    def next_state(self, pointer):
        if self.current_state(pointer) is None:
            return self.get_start_state()

        if pointer.jump is None:
            return None

        return self.knowledge_base[self.knowledge_base[pointer.jump].state_to]

    def step(self, pointer):
        next_state = self.next_state(pointer)
        # next_jump = []
        new_pointer = pointer
    
        state = self.current_state(pointer)
        if next_state:
            state = next_state
            new_pointer = pointer.change(state=next_state.uid, jump=None)
    
        next_jump = self.get_next_jump(self.current_state(new_pointer))
        if not next_jump:
            raise ValueError(self.current_state(new_pointer))
    
        return new_pointer, state, next_jump

    def get_next_jump(self, state):
        jumps = self.get_available_jumps(state)
        if not jumps:
            raise ValueError(state)
        return jumps

    def get_available_jumps(self, state):
        if isinstance(state, facts.Choice):
            return [default for default in self.knowledge_base.filter(ChoicePath) if default.choice == state.uid]

        # if isinstance(state, facts.Question):
        #     condition = all(requirement.check(self.interpreter) for requirement in state.condition)
        #     return [answer for answer in self.knowledge_base.filter(facts.Answer) if
        #             answer.state_from == state.uid and answer.condition == condition]

        return [jump for jump in self.knowledge_base.filter(Jump) if jump.state_from == state.uid]

    def need_concrete_answer(self, pointer):
        state = self.current_state(pointer)
        if isinstance(state, facts.Choice):
            return True
        return False
        
        
class BaseView:
    def __init__(self, uid):
        self.uid = uid
        
        
class Start:
    def __init__(self, uid):
        self.uid = uid
    

class Finish:
    def __init__(self, uid, results, start):
        self.uid = uid
        self.results = results
        self.start = start


class ChoicePath:
    def __init__(self, uid, choice, state_to, label):
        self.uid = uid
        self.choice = choice
        self.state_to = state_to
        self.label = label

    
class Jump:
    counter = 0
    
    def __init__(self, state_from, state_to, label):
        self.uid = "jump#{}".format(self.counter)
        self.state_from = state_from
        self.state_to = state_to
        self.label = label
        self.__class__.counter += 1
        

class State:
    def __init__(self, uid):
        self.uid = uid
        
    
class User:
    def __init__(self, name):
        self.name = name
        self._pointer = facts.Pointer()
        
    def update_pointer(self, new_pointer):
        self._pointer = new_pointer
        
    def get_pointer(self):
        return self._pointer
    
        
class UserManager:
    def __init__(self):
        self._users = {}
        
    def register(self, chat_id, user):
        if chat_id in self._users:
            print('already register')
            return
        self._users[chat_id] = user
        
    def get_user(self, chat_id):
        return self._users[chat_id]
    
    
steal_choice = facts.Choice(uid='st_steal')
start = Start(uid='st_start')
values = [
    start,
    State(uid='st_wait'),
    steal_choice,
    ChoicePath(choice=steal_choice.uid, uid='st_steal.steal', state_to='st_finish_stealed', label='ограбить'),
    ChoicePath(choice=steal_choice.uid, uid='st_steal.deliver', state_to='st_finish_delivered', label='сопроводить'),
    
    Finish(uid='st_finish_delivered', results=(), start=start.uid),
    Finish(uid='st_finish_stealed', results=(), start=start.uid),

    Jump(state_from='st_start', state_to='st_wait', label="Приблизиться"),
    Jump(state_from='st_wait', state_to='st_steal', label="Дальше"),
    
]

kb = KnowledgeBase()
kb.create_story(values)
story = Story(kb)
#
# if __name__ == "__main__":
#
#     import time
#     pointer = facts.Pointer()
#     while not story.is_processed(pointer):
#         new_pointer, current_action, possible_jumps = story.step(pointer)
#         # print(possible_jumps)
#         jump = random.choice(possible_jumps)
#         pointer = new_pointer.change(state=jump.state_to)
#         print(current_action)
#         time.sleep(0.5)
#
#     print(story.current_state(pointer))

