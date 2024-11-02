# Aidan - Approaching Specialization
There's a bit of a problem that I'm trying to solve. Because I like the idea of Simple Agent staying as essentially a core library, which can be extended and adopted by and for various domains of endeavor. As a developer, it's tempting for me to equip it with developer tools, however that's likely not the right way forward entirely. Additionally, tools like web searching and such seem like a great idea, but I'm not sure that they actually would be.

Thus, I like the idea of the agent being capable of fulfilling different "roles" depending on the task at hand. For example, it might take the "developer" role at some point to be capable of carrying out development tasks. At another point, it might take the "researcher" role to be capable of browsing sources, compiling research and generating reports. It's worth noting that the nature of these "roles" isn't the same as a multi-role team, and it's hard to say exactly what it *will* look like.

However, what we do know is the following:
- A flat list of tools does not scale well
- "Toolboxes" can be specialized towards a specific role
- Some tools are best to always have, like sending user's messages and other interfacing tools
- Tools can be grouped by problem set

So, here's what I'm thinking. We already have a data structure called "Toolboxes". The toolbox is the managed set of tools available to the agent to complete its tasks. The "toolbox" is given to the agent in `agent.py` and is listed to the llm.

Since you can create toolboxes for any configuration of tools, all we need to do is create "Roles", which will have toolboxes and identities attached. That way, the agent can adopt new identities on the fly.
