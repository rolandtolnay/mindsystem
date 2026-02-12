# The New Paradigm of Agentic Coding

We're entering a new paradigm of agentic coding. I'm not talking about the very powerful but very dangerous Maltbot or previously Cloudbot. More on that later. I'm talking about new tools for engineers to orchestrate intelligence. The new Claude code task system is going under the radar in a massive way, probably because of all the Cloudbot hype.

But this feature hints at the future of engineering work. I have two prompts to show you that you can use to extend your ability to build with agents and it's all based on this new Claude code task system. This changes the workflow of engineering in a pretty significant way and really it's not getting enough attention. I want to focus on this in a very anti-hype way.

I have one metaprompt and one plan to share with you that can push what you can do with agents in a Claude code instance. We will slash plan, but this isn't an ordinary plan. We're going to plan with a team. We have a user prompt and an orchestrator prompt.

This prompt will showcase you can now reliably and consistently create teams of agents. More agents, more autonomy, and more compute doesn't always mean better outcomes. What we want is more organized agents that can communicate together to work toward a common goal.

If you want to understand how to use the Claude code task system at scale reliably and consistently to create teams of agents, stick around and let's jump right in.

## Plan with Team Components

Let's take a look at plan with team. This isn't like most prompts you've seen. This prompt has three powerful components to it:

- Self-validation
- Agent orchestration
- Templating

The first thing you'll notice here is that we have hooks in the front matter. This agent is self validating. In fact, it has specialized scripts that it uses to validate its own work. You can see here we have validate new file and we have validate file contains. So on the stop hook once this agent finishes running, it's going to make sure that it created a file of a specific type in a specific directory and it's going to make sure that it contains specific content. This is very powerful. Now we know for a fact that this plan was created.

If we close this, we can see that our plan has been created and it's been validated. And so now the next step is we're going to actually kick this off. And you can see our agent has done something really interesting here. We have a team task list. Every task has an owner. So this is not an ordinary sub agent prompt. This task list has specific team members doing specific work all the way through.

We're using two specific types of agents. We're going to break down in just a second a builder agent and a validator agent. We're going to go ahead and kick off this prompt and we're going to actually start building this out.

## Building the Task List

We'll look at the spec. This is the second prompt that we're going to look at and we're going to understand why this generated prompt from our meta prompt is so unique. You'll notice here it is building up that brand new task list. It's just going to keep stacking on the brand new task list. We're also going to look at the actual tools that this agent is running to put together this team of agents and to communicate the results. We have five more pending. A lot of work is getting stacked up here.

Now we're getting the dependency blockers. Not only is our agent planning out work and building a team, it's also setting up the tasks and the order that the tasks need to operate in. You can see here our first five or six tasks. These can run in parallel. They're building out the brand new hooks.

So to be clear here, what we're doing is I have this code base on my repo cloud code hooks mastery. Last update was five or six months ago. We're going to go ahead and update the documentation and update some of the code. This is a very common engineering workflow that you would run that you would enhance with agents. You need to update old code to update and reflect changes and new documentation.

Right now we're kicking off a bunch of agents to run in parallel. Sub agent text to speech responses are going to keep streaming in here. Every sub agent that completes is going to summarize their work as well. I have this built into the sub agent stop hook.

This work is just going to continue to stream in.

## Agent Orchestration and Task Management

The next important piece is of course agent orchestration. If we collapse everything here, you can see a classic agentic prompt format. We have our purpose. We have our list of variables. We have our prompt format and our orchestration prompt. We have our instructions. Inside of the instructions, we have an additional new block, **team orchestration**.

And so here we're starting to detail these new task management tools:

- Task create
- Task update
- Task list
- Task get

This is how the task system works. This is everything that our primary agent needs to conduct, control, and orchestrate all possible sub agents. The communication happens through this task list. This is a huge stepping stone from just calling ad hoc sub agents without a common mission without task dependencies and without a way to communicate to each agent that the work is or isn't done yet.

What's really important here is in our workflow. If we look at our agentic prompt format here where we're detailing the steps that we want our plan with team prompt to set up, we can see something really interesting. In step four and five, we're doing two important things:

1. Defining team members using the orchestration prompt if provided
2. Defining step-by-step tasks

So our plan is going to use team orchestration. The primary agent that is actually creating this plan is going to build a team and then give each team member a task step by step.

This is unique. Our previous planning prompts that we would set up that create the plans for us that research the codebase, we would have to specify exactly what agent was running, exactly how we wanted to specialize that workflow, and then it would run in some top to bottom format that you would have to strictly organize. Now, with teams and with the task list, we can teach our primary agent how to create plans that also contain individual team members.

## Templating in Agent Prompts

The last very important piece of this prompt is that we are templating. So this metaprompt is actually a **template metaprompt**. This is a big idea we talk about in tactical agentic coding. We're teaching our agents how to build as we would. We have a plan format and the plan format actually has embedded prompts inside of it. Replace nested content with the actual request inside of it.

So our plan is going to come out to task name. If we open up specs, you can see we have hooks update with team. If we go side by side, you can see exactly how this is getting templated. Here's the plan name. Here's the task description. And then we're having our agent fill out the task description. So this agent is really building as we would.

You want to be teaching your agents how to build like you would. This is the big difference between agentic engineering and vibe coding and slop engineering. When you're running a prompt to a random tool like Clawbot or insert whatever tool, whatever agent, and you don't know what the agent is actually going to do or how it's going to do the work, the results can be anywhere from exactly what you wanted to not so great to this doesn't work at all.

As models progress and become more proficient, you'll be able to prompt with less effort, with less thought. But if you're doing real engineering work, you want to be going the opposite direction. You want to know the outcome that your agent is generating for you. You can do that with the **template prompt**, specifically the **template meta prompt**. This is a prompt that generates a new prompt in a very specific, highly vetted consistent format.

We have our objective on both sides. We have our problem statement. We have the solution approach. But where things get interesting is here. We have team orchestration. If we search for this, I know for a fact that team orchestration will be inside the generated prompt. Why is that? It's because remember that this stop hook ran self validation. It's running validate file contains. It's making sure that it's in the specs directory. It's a markdown file and it contains these sub points. I'm making absolute sure that the file that was generated has the correct section. If it doesn't, this script here, validate file contains, is going to spit back out instructions for this planner agent. This is very powerful.

We're combining specialized self validation with this new team orchestration with powerful templating. Templating is something we discuss at length in tactical agent coding because it allows you to teach your agents to build like you would. But this team orchestration section is very powerful.

You can see here this is part of a template, but it's raw text. Our agent copied it as is per the instructions. But then here our agent starts building out the team members. On the left we have the template metaprompt. On the right, we have the generated plan file that our agent is running.

You can see builder, validator, builder, validator, builder, validator, on and on and on. I have two specific agents that I'm using in this workflow. I think this is going to be the most foundational bare minimum that you're going to want to have set up. A builder and a validator. An agent that does the work and an agent that checks the work. I'm 2xing the compute for every single task so that we build and then we validate.

In our prompt template, we have our builder and then we're specifying the name, role, agent type, and if it should resume if something goes wrong. This is all just about filling in the variables, filling in the specification for the team that's going to execute this work.

We also have the step-by-step tasks, which breaks down the actual workflow. We're just going through step by step and our agents are going through the work that they need to do. This is the task list that we're building up, working step by step. We built this into a reusable prompt that we can deploy over and over and over.

It's always one thing to just open up a terminal and start prompting something, but we can do much better than this. Build reusable prompts, build reusable skills. I think a lot of engineers in the space already understand this as a foundational concept, but you can push it further.

Remember this metaprompt has three powerful components:

1. It is self-validating
2. It is building a team and it has specific instructions on how to build a team
3. If the orchestration prompt is provided, that orchestration prompt is going to help guide how the planner builds the team

And then we're also templating. So this is a template metaprompt. It might sound like a super fancy term, but it's not. It's a prompt that generates another prompt in a specific format. It's quite simple, but it's very powerful. This is advanced agentic prompt engineering. Once you see this and once you start building these out, it becomes second nature.

## The Cloud Code Task System

What does the new Cloud code task system look like? How is this unique? What we're doing here is we're actually building up a task list and a dedicated team to handle the individual tasks. Now, this is vastly superior to the previous generation to-do list and previous generation sub agent colon via the task tool because you can set up tasks that run in specific order that block and that depend on other tasks to be complete.

Not only that, this allows for massively longer running threads of work because your primary agent can orchestrate a massive task list, kick it off, and then as agents complete it will receive specific events. As sub agents complete work, they will actually ping back to the primary agent that accomplished the work. The primary agent can react to it in real time. You don't have to sit, you don't need to add bash, sleep, loops. The task system handles all of that.

The key task system functions are:

- **Task create** - Creates a new task
- **Task get** - Retrieves a task
- **Task list** - Lists all tasks
- **Task update** - Updates a task with additional details

Task update is the big one. You'll create a task and then update the task with additional details. The powerful thing about this is that your primary agent and your sub agents can use these tools to communicate to each other. That's what's happening here with these tools. Task update is going to be the big one because this allows the sub agents and the primary agent to communicate the work.

This unlocks powerful workflows. We can now set up multi-agent teams with even more than one primary agent. You kick off a larger plan, a larger set of work. Your agents will start working on it. The agents will then complete their work and then the blocked tasks are now unblocked and the agents will continue working through those piece by piece, sending messages that they finished once the task list is complete.

And really, as work completes, the primary agents will be alerted. You can spin up as many agents as you want. Notice how this is looking a lot like the agent threads that we talked about a couple weeks ago. Thread-based engineering is a powerful mental framework to think about how work gets complete.

Here's the workflow:

1. You prompt your agents
2. Your agents create a large task list
3. Your agent teams, your sub agents, then accomplish the work in order reviewing, checking each other's work
4. If you set up the right reviewer agents, they unblock the next task, and so forth
5. They communicate when their work is done
6. The task list system will ping back to the agent
7. Your agent will respond to you once the work is done

This is the powerful task system and it becomes even more powerful when you deploy it and build it into a reusable prompt that you can run over and over and over.

## What Our Agent Built

Let me check out what our agent did for us. It added and updated the documentation for this codebase. You can see all the files changed. You can see we have a bunch of new status lines. We got those new hooks that just weren't there. We updated the readme. We have that new spec. And we have our new JSON file.

You can see those new hooks there:

- Session end
- Permission request
- Sub agent start
- Setup

And we have a bunch of new hooks. Every one of these hooks should have their own log file. If we open up this prompt here, let's understand how these two agents work together. The planning agent built a team. Why is this different? Why is this more powerful? Because you can build specialized agents that do one thing extraordinarily well.

If we look at the team members, you can see team members is a variable here and it's something that we detail inside of the workflow. In step four, we say this exactly: Use the orchestration prompt to guide team composition. Identify from cloud agents team markdown. We're looking at agents only in the specific directory or we're using a general purpose agent.

I have just two teammates. Two specific types of agents that this codebase has access to:

1. Builder
2. Validator

The purpose of the builder is just to focus on that one task to build it and then to report its work. Our builder goes a little further. You can now build specialized self validation into every one of your agents.

Our builder agent after it runs, on post tool use write edit, it's going to look to see if it's operating in a Python file and then it's going to run ruff and type. It's going to run its own code checkers basically. These can be any types of code validation that you want. The powerful thing here is that we've built in a micro step of validation inside the builder on its own.

And then we have a higher level validator agent that's just going to make sure that the task was done properly. Make sure that the code is complete, make sure that it can run whatever validation it needs to validate that the builder did actually do the work.

I really like this kind of two agent pairing. We're basically increasing our compute to increase the trust we have that the work was delivered. If we had a specific type of validation, we could also build out tools to give this agent specialized tools to make sure that the builder did his job properly. I think this is probably the simplest team combination you can build.

Of course, there are other things: QA tester agents, reviewer agents, deploy agents, blog monitoring agents. You can build all types of agent teams, but I think these are the two most foundational. Have an agent build the thing and then have another agent validate the thing. Very powerful.

This is what our primary agent that was doing the planning work, with the template metaprompt. This is what it used to actually put together the team. Every one of these agents was unique. We built a session end builder for this session end hook and then we built the corresponding validator. Same thing with permission request builder and then permission request validator.

And this is where it gets really powerful. In the step-by-step task, you can see here we have build workflows. Build, build, build. And then after six, we have validators. Our agent is doing compilation on the code to make sure that it's legit. And then we have additional validation steps down here.

We have all of our logs for each one of these new methods. Every one of the new ones has a corresponding log file. Session end, permission request, post tool use failure. All have log files created.

Then in step 15 and 16, we're going to update the readme. We have simple validation here to check this. We can open this. And then we can search for one of these tools that weren't previously documented. If we search for post tool use, you can see all of our documentation got edited.

We got a bunch of new status lines. We got our file references updated. We have our new documentation for these hooks. The settings file got updated as well. You can see new hooks were added.

This was a relatively simple task for Opus to handle, especially with it deployed across multiple agents, focusing on one specific task at a time. That's another huge value proposition of this system. Every one of your agents has a focused context window doing one thing extraordinarily well. This is something we talk about all the time in tactical agent coding. The more agents you have with focus context windows doing one specific thing, the better.

This multi-agent task system is perfect for that. Your top level planner orchestrator agent writes the plan. You want to refresh the context after that, kick it off in a new agent to do the building that was inside of the plan. Once they do that, your multi-agent system's task list and the individual agent teams that you assign the work to, they take care of it from there.

## When to Use This Task System

When should you use this task system? This is on by default if you write a large enough prompt Claude code and Opus it knows it has access to these tools. That's a little bit more valuable but I think if you're really pushing and you're really scaling what you can do with agents you're going to want to build out a metaprompt like this. It's a prompt that builds a prompt.

With agentic coding there are two primary constraints:

1. Planning
2. Reviewing

You're probably spending most of your time planning or reviewing if you're doing things right. This prompt and this new set of tools really helps us in the planning phase. We can build out specialized agents that are self-validating. Every one of them is checking their own work. This is super important.

What you can do with your team members, your agents that are built for specific purposes, is build unique workflows where you think about the combination of running multiple agents together that outperform a single one. We do build, we do test, we do build, we do review. We have a documentation agent that is all about documenting. That's another direction we can go with this.

Our validator is just reporting if the thing was built right. If it was, we report success. If it wasn't, we report failure. A very powerful dedicated agent just for validating work.

The orchestrator prompt becomes even more important. Remember we pass in two prompts: what we wanted to build and then the actual orchestration prompt. The orchestration prompt details exactly what this looks like. "Create groups of agents for each hook, one builder and one validator."

So this is our orchestration prompt. This is our high-level prompt that gets boiled down into a low-level prompt thanks to our metaprompt. In the orchestrator prompt, we're actually helping our agent guide how to build the team that does the work. This is a new paradigm of multi-agent orchestration that's emerging. This is one way you can use it repeatedly, consistently, and reliably. It also gives you flexibility because you can pass in that orchestration prompt.

A couple big ideas we're hitting on here:

- Self-validation
- Multi-agent orchestration
- Building it into our reusable prompts

A lot of engineers are going to miss this. Please don't be one of them. You can build team orchestration into your reusable prompt so you get the value every single time. It only takes one time to build out a great prompt. That upfront investment is really where you want to be spending more and more of your time.

As mentioned in tactical agentic coding, you want to be building the agentic layer of your code base. Don't work on the application anymore. Work on the agents that build the application for you.

## The Path to Agentic Mastery

There's a lot of value embedded in that. There's a lot of what we're seeing coming out with multi-agent orchestration, which the Claude code team is not documenting very well. I wish they would really up their documentation on this stuff.

This task feature is pushing in the direction of multi-agent orchestration. Remember, in the beginning, you have a base agent. Then you learn how to use it better by context engineering and prompt engineering. Then you add more agents. Very powerful. After you add more agents, you customize them. And then lastly, you add an orchestrator agent to help you conduct all of them.

And that's what we're turning our primary agent into. Your primary agent when they're working with this task list, when they're working with your agent teams, they are orchestrating.

Now, there's levels to this. We built our own multi-agent orchestration system inside of Agentic Horizon. I'll link the course in the description if you want to push what you can do with agentic engineering further.

I'll leave this prompt in the cloud code hooks mastery codebase for you. If you want to check it out, if you want to understand how you can build template meta prompts that encode your engineering, this is very powerful.

## The Hype vs. The Fundamentals

I think there's a lot of hype right now in the tech industry. There's a lot of slop engineering and vibe slopping coming out by a lot of people just jumping onto these super high-level abstract tools like Moltbot. I have nothing against this thing. I can see why people are really interested. It's very powerful. This thing's gone super viral, but I am concerned about an over reliance on tools like this without understanding the pieces of it.

If you're an agentic engineer, if you're an engineer that has been learning to really use agents and build proficient systems that operate with and without you, go crazy with tools like this. You know what's happening underneath the hood. It's everyone else that I'm worried about. They have no idea what's going on underneath the hood.

If you're trying to learn how to build with agents, it's all about the core four:

- Context
- Model
- Prompt
- Tools

It's about learning to leverage these fundamental levers of agentic coding, the fundamental pieces of building with agents. It comes down to:

- Reusable prompts
- Building out your own specialized agents
- Building out AI developer workflows (ADWs as we call them in TAC)

It's all about knowing what you're doing and teaching your agents how to do it.

There's going to be a big gap between engineers that turn their brain off and engineers that keep learning and keep adding to their stack of agentics, their patterns and tools that they can use to teach their agents how to build on their behalf. I'm not saying don't use agents. I think this tool and other tools like it, they're incredible. What I'm saying is know how to use the primitives and the leverage points of agentic coding. The foundational pieces that make it all up.

Because if you do that, you'll be able to hop from tool to tool to tool to feature to feature to feature. This tool is a great example. This system that the Claude code team has built out, it's not new. Open source tools have had this, but what they've done here is standardized it and made it accessible through the best agent coding tool. That's worth paying attention to. That's worth learning. These are just tools and prompts. This entire feature set is just tools and prompts.

If we needed to, if you wanted to, we could step away from Cloud code. We could build it into another tool if needed. Thankfully, we don't have to. They built it in. This is the Claude Code task system. You can use this to build specialized agent teams when you combine it with a powerful metaprompt, a prompt that builds a prompt. When you template and add self validation into your agentic systems, these are powerful trends.

Make sure to like and comment. Let the algorithm know you're interested in real hands-on agentic engineering. I want to push back against some of this insane AI hype that's going on right now. Let's stay close to the fundamentals. Let's stay close to what makes up the agent at a foundational level while increasing what we can do with this.

You know where to find me every single Monday. Stay focused and keep building.