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

start = Start(uid='intro')
call_colonel = State(uid="call_colonel")
# call_general = State(uid="call_general")
call_captain_new = State(uid="call_new_captain")
call_new_general = State(uid="call_new_general")
call_new_lieutenant = State(uid="call_new_lieutenant")
call_new_colonel = State(uid="call_new_colonel")


general_choice = facts.Choice(uid="general_choice")
gp1 = ChoicePath(choice=general_choice.uid, uid='general_choice.help', state_to='call_captain', label='Молча повиноваться')
gp2 = ChoicePath(choice=general_choice.uid, uid='general_choice.end', state_to='dismiss_and_finish', label='Отказаться и ждать что будет')


knock_to_ceo = State(uid="knock_to_ceo")
call_captain = State(uid="call_captain")


colonel_choice = facts.Choice(uid="colonel_choice")
cc1 = ChoicePath(choice=colonel_choice.uid, uid='colonel_choice.help', state_to='call_captain', label='Да чего уж, поможем')
cc2 = ChoicePath(choice=colonel_choice.uid, uid='colonel_choice.knock', state_to='knock_to_ceo', label='Втихую настучать главнокомандующему')


knock_to_general = State(uid="knock_to_general")
call_lieutenant = State(uid="call_lieutenant")

captain_choice = facts.Choice(uid="captain_choice")
cpc1 = ChoicePath(choice=captain_choice.uid, uid='captain_choice.help', state_to='call_lieutenant', label='Безвозмедно помочь')
cpc2 = ChoicePath(choice=captain_choice.uid, uid='captain_choice.knock', state_to='knock_to_general', label='Доложить Генералу о произволе')


call_corporal = State(uid="call_corporal")
knock_to_colonel = State(uid="knock_to_colonel")

lieutenant_choice = facts.Choice(uid="lieutenant_choice")
lc1 = ChoicePath(choice=lieutenant_choice.uid, uid='lieutenant_choice.help', state_to='call_corporal', label='Рад служить!')
lc2 = ChoicePath(choice=lieutenant_choice.uid, uid='lieutenant_choice.knock', state_to='knock_to_colonel', label='Доложить Полковнику о неуставных отношениях')


call_newbie = State(uid="call_newbie")
knock_to_captain = State(uid="knock_to_captain")

corporal_choice = facts.Choice(uid="corporal_choice")
corpc1 = ChoicePath(choice=corporal_choice.uid, uid='corporal_choice.help', state_to='call_newbie', label='Подъём дух, деревья сами себя не срубят!')
corpc2 = ChoicePath(choice=corporal_choice.uid, uid='corporal_choice.knock', state_to='knock_to_captain', label='Товаришь капитан, разрешите доложить о нарушениях...')


newbie_choice = facts.Choice(uid="newbie_choice")
np1 = ChoicePath(choice=newbie_choice.uid, uid='newbie_choice.help', state_to='success_finish', label='Есть рубить отсюдова и до обеда!')
np2 = ChoicePath(choice=newbie_choice.uid, uid='newbie_choice.knock', state_to='fail_finish', label='Спасибо, хватит с меня, пора валить!')


values = [
    start,
    call_colonel,
    call_captain_new,
    call_new_general,
    call_new_lieutenant,
    call_new_colonel,
    general_choice,
    gp1,
    gp2,
    knock_to_ceo,
    call_captain,
    colonel_choice,
    cc1,
    cc2,
    knock_to_general,
    call_lieutenant,
    captain_choice,
    cpc1,
    cpc2,
    call_corporal,
    knock_to_colonel,
    lieutenant_choice,
    lc1,
    lc2,
    call_newbie,
    knock_to_captain,
    corporal_choice,
    corpc1,
    corpc2,
    newbie_choice,
    np1,
    np2,
    Jump(state_from="intro", state_to="call_colonel", label="Позвать полковника"),
    
    # Jump(state_from="call_general", state_to="general_choice", label="Надо подумать."),
    Jump(state_from="call_new_general", state_to="general_choice", label="Выбрать бы правильно..."),
    
    Jump(state_from='call_colonel', state_to='colonel_choice', label="Что выбрать полковнику?"),
    Jump(state_from='call_new_colonel', state_to='colonel_choice', label="Аккуратно, не торопимся"),
    
    Jump(state_from="call_lieutenant", state_to="lieutenant_choice", label="Честь имею!"),
    Jump(state_from='call_new_lieutenant', state_to='lieutenant_choice', label="Спокойствие, главное спокойствие"),
    
    Jump(state_from="call_captain", state_to="captain_choice", label="Хммм..."),
    Jump(state_from="call_new_captain", state_to="captain_choice", label="А-га..."),
    
    Jump(state_from="call_corporal", state_to="corporal_choice", label="Товаришь ефрейтор, на минуту"),
    Jump(state_from="call_newbie", state_to="newbie_choice", label="А что если..."),
    
    
    Jump(state_from="knock_to_ceo", state_to="call_new_general", label="Вызвать новоиспечённого генерала"),
    Jump(state_from="knock_to_general", state_to="call_new_colonel", label="Полковника сюда"),
    Jump(state_from="knock_to_colonel", state_to="call_new_captain", label="Капитан!"),
    Jump(state_from="knock_to_captain", state_to="call_new_lieutenant", label="Найти лейтенанта, живо!"),
    
    Finish(uid='dismiss_and_finish', results=(), start=start.uid),
    
    Finish(uid='success_finish', results=(), start=start.uid),
    Finish(uid='fail_finish', results=(), start=start.uid),
    
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

