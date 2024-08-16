Aidan: How should LLMs handle file editing?
---
How could I think about file editing for an LLM? It's a bit different, inherently, from how a human might do it. Our systems are designed around our handy fingers, and so we can perform small operations, quickly, with a quick feedback mechanism. When we type a word, we see it appear character by character on the screen. We make mistakes often, so it's important to have backspace, and other tools like Vim allow for increased fluidity to operations.

However, an LLM isn't the same thing as a person. First, for an LLM to perform *any* operation, it has to perform a completion, and a function call. This means that maximizing the effectiveness of a SINGLE operation becomes worthwhile. Additionally, an LLM can generate a lot of text, very quickly, and does so without typos or other mistakes. Additionally, LLMs work most accurately when given reference points clearly in their context. Therefore, maximizing reference points, and allowing for simple editing procedures which are also effective, is the goal.

For that matter, I think that *line-based editing* is the best approach. Essentially, the LLM will say "replace what is currently between this line and this line, with this new content". Then, the current content between those lines would be deleted, and whatever content is provided would populate that new area. Therefore, there'd be a sort of "selection", and then a "replacement", which could be any string.

So essentially, pseuodocode would look like this:

```
function edit_file(selection: str)

```
