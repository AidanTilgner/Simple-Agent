Aidan: Defining the loop
---
I want to discuss the agent loop. How exactly should we think about it?

For my part, the agent loop can be broken down into 3 main components:
- Prompt
- Inference
- Action

These components are made up of various subcomponents. For example, the prompt, which is essentially the center for perception by the model, can be broken further into three subcomponents:
1. Environment: everything within the agent's perview, which it is capable of navigating
2. Memory: things that the agent remembers over time
3. Agency: the agent's direction forward

Inference, can be understood as the formation of the prompt, and sending that to the language model of choice. Agency, therefore, can be understood as a set direction, which informs the language model at inference as to what it should be striving for. Agency could potentially be broken down further:
1. Immediate: The most pressing direction, the next step, etc
2. Task-Level: The general task which needs to be completed
3. General: The goal under which each task is set, could be tuned to a specific scope

Agency, therefore, does need to be dynamic at some level. The general agency might be best understood as the system prompt, and generally unchanging. The task-level and immediate agency, however, are best understood rather as something which dynamically changes. How exactly this should be handled is a bit less clear to me. However, the agency is also I think where we find the control over whether action should be taken or not.

Additionally, the immediate level agency does not need to be clearly defined, as immediate level agency would be decided by the reasoning engine. Essentially, whatever action it decides to take is the immediate level agency. This means that the general and immediate level agency are already accounted for, as the system prompt and tool calls take those places. That means that the only thing we need to account for in terms of agency is the task-level, which I'm not entirely clear on deciding.

Aidan: Defining tasks
---
If the task is the only part that needs to be dynamically defined by the system in the creation of a prompt, we need to decide what the system is to do that.

There needs to be something that can 1) create the tasks, and 2) decide whether a task has been completed

I like the idea of multiple tasks being available as well. Usually there isn't just one task available at hand, but multiple. So the agent should be capable of holding multiple independant tasks in perception, taking actions to complete each of them, and marking them complete. Each "task" should be a set of dependant requirements, which together make a coherent completion criteria.

If two requirements don't contribute to the same task, then they shouldn't be grouped together. In this sense, a task could be seen as having the following shape:

```json
{
  id: "task-1",
  "description": "Do the thing",
  "requirements": [
    "Requirement number 1",
    "Requirement number 2"
  ],
  "completed": false,
}
```

I think that we have two general options here:
1. A discrete system component which analyzes messages, and cross-references with the task list to perform the following operations:
  - Task Creation: creates a new task if stimuli suggests that one should be created
  - Task Completion: completes tasks if these tasks should be considered complete based on messages
2. Two tools which are given to the normal reasoning engine, capable of creation or completion of tasks

Of these, I'm inclined, for the sake of simplicity, to favor the second approach. If we can simply define two new tools which complete or create tasks, then that's all the management which I believe would be required. It may be worth creating a divergent branch in the future to test the first approach, however. I think that it might be a bit too convoluted to have it be a different system handling the task logic.

Aidan: Handling control flow
---

I'm trying to figure out how to handle control flow of the agent loop. Everything centers around the idea of tasks. However at the same time, I want to think about the agent iterating vs not iterating as being the difference between being awake and going to sleep. Therefore, I'd need to come up with discrete criteria under which the sleep state would be achieved, or the awake state.

**Awake**
The agent should be awake if there is stimulus for it to respond to, or duties to fulfill. This essentially means that there may be unseen messages, or tasks to be completed. Even in the case where a message is sent, the agent should still continue fulfilling tasks until all tasks are considered complete. So the logical criteria are as follows:
- Open tasks remain
- New stimuli exists such as unseen messages

**Asleep**
On that note, however, the restful state must be reached at this point. The difficulty here will be in having the agent sleep, without compromising its ability to respond to stimulus. Let's just start by defining under which conditions sleep makes sense. If there are no open tasks, then there is no reason to go on trying to complete them. If there is no new stimuli, then there is no reason for the agent to attempt to respond. Therefore, if there are no incomplete tasks, and no new stimuli, then there shouldn't be any reason to sleep. The logic conditions are as follows:
- There are no open tasks
- There is no new stimuli
