# Advanced Context Engineering for Agents

*Talk by Dex, Founder of Human Layer*

---

## Introduction

Hi everybody. My name is Dex. I'm the founder of a company called Human Layer. I was in the fall 20. Apparently we're all YC founders on stage today. I was in the fall 24 batch.

---

## A Brief History of Context Engineering

I'll give you a little itty bitty history of context engineering in the term. Long before Toby and Andre and Walden were tweeting about this in June. In April 22nd, we wrote a weird little manifesto called 12factor agents principles of reliable LLM applications. And then on June 4th, and shouts out, I did not know Swix was going to be here, but he's getting a shout out anyways. Changed the title of the talk to context engineering, to give us a shout out for that.

So everyone's been asking me what's next. We did the context engineering thing. We talked about how to build good agents.

---

## Notable Talks from AI Engineer

I will point out my two favorite talks from AI engineer this year. Incidentally, the only two talks with more views than 12 factor agents.

### Sean Grove - "The New Code"

Number one is Sean Grove, the new code. He talked about how, if I can figure out how to use this. He talked about how we're all vibe coding wrong and how the idea of sitting and talking to an agent for two hours and figuring out and exactly specifying what you want to do and then throwing away all the prompts and committing the code is basically equivalent to if you're a Java developer and you spend six hours writing a bunch of Java code and then you compile the jar and then you checked in the compiled asset and you threw away the code.

In the future where AI is writing more and more of our code, the specs, the the description of what we want from our software is the important thing.

### The Stanford Study

And then we had the Stanford study which was a super interesting talk. They ingested data from 100,000 developers of all giant enterprises down to small startups. And they found that like AI engineering and software leads to a lot of rework. So even if you get benefits, you're actually throwing half of it away because it's kind of sloppy sometimes.

And it just doesn't work for complex tasks or brownfield tasks. So old code bases, legacy code bases, things like that. And especially for complex brownfield tasks, it can be counterproductive. Not even that it doesn't really help that much, but it can actually slow people down.

And this kind of matched my experience, talking to lots of smart founders. It's like, yeah, coding agents, it's good for prototypes. Even Amjad from Replet, was on a podcast six months ago and he's like, yeah, our product managers use this to build prototypes and then when we figure it out, we give it to the engineers and they build production. Doesn't work in big repos, doesn't work for complex systems. Maybe someday when the models get smarter, we'll be able to have AI write all of our code.

But that is what context engineering is all about. How do we get the most out of today's models?

---

## The Spec-First Development Journey

So I'm going to tell you a story about kind of a journey we've been on the last couple months of learning to do better context engineering with AI generated code.

So I was working with one of the best AI coders I've ever met. They were shipping every couple days I would get a 20,000line PR of Go code and this was not a CRUD app or a Nex.js API. This was complex systems code with race conditions and shutdown order and all this crazy stuff.

And I just couldn't review it. I was like, I I hope you know I'm not going to read this next 2,000 lines of Go code.

And so we were forced to adopt spec first development because it was the only way for everyone to stay on the same page. And I actually learned to let go. I still read all the tests, but I no longer read every line of code because I read the specs and I know they're right. And it took a long time and it was very uncomfortable. But over 8 weeks or so, we made this transformation and now we're flying. We love it.

---

## What I Learned

So, I'm going to talk about a couple of things we learned on this process. I know it works because I shipped six PRs last Thursday and I haven't opened a non-markdown file in an editor in almost two months.

### Goals

So the goals, I didn't set these goals. I was forced to adopt these goals. But the goals are:

- Works well in big complex code bases
- Solves big complex problems
- No slop, we're shipping production code
- Everyone stays on the same page
- Oh, and spend as many tokens as possible

---

## Advanced Context Engineering for Coding Agents

This is advanced context engineering for coding agents.

### The Naive Approach

I want to talk about the most naive way to use a coding agent, which is to shout back and forth with it until you run out of context or you give up or you cry. And you say, "No, do this. No, stop. you're doing it wrong.

### Being Smarter About Restarts

You can be a little bit smarter about this. Basically, if you notice the agent is off track, a lot of people have done this. I've seen some people from OpenAI post about this. This is pretty common. If it's really screwing up, you just you just stop and you start over and you say, "Okay, try again, but make sure not to try that because that doesn't work."

If you're wondering when you should consider starting over with a fresh context, if you see this, it's probably time to start over and try again.

---

## Intentional Compaction

We can be smarter about this though. And this is what I call intentional compaction. So, it's not just start over and I'm going to tell you something different. Put my same prompt in with a little bit of steering.

But even if we're on the right track, if we're starting to run out of context, be very intentional with what you commit to the file system and the agents memory. I think slashcompact is trash. I never use it. We have it write out a progress file very specifically, which is like my vibe of what I found works really well for these things. And then we use that to onboard the next agent into whatever we were working on.

### What Are We Compacting?

What are we compacting? Why? Like how did I get to this? Lots of people have instincts about what works here.

So the question is like what takes up space in the context window?

- Looking for files
- Understanding the flow
- Doing edits
- Doing work
- If you have MCP tools that return big blobs of JSON, that's going to flood your context window with a bunch of nonsense

So what should we compact? We'll get on to like what exactly goes in there. But it looks something like this. And I'll talk about the structure of this file a little bit more.

---

## Why We're Obsessed with Context

Why are we obsessed with context? Because LMS are pure functions. I think Jake said a lot of interesting things about this. The only thing other than like training your own models and messing with the temperature, the only thing that improves the quality of your outputs is the quality of what you put in, which is your context window.

And in a coding agent, your agent is constantly looping over determining what's the right next tool to call, what's the right next edit to make, and the only thing that determines its ability to do that well is what is in your context window going in.

And we'll throw this one into everything is context engineering. Everything that makes agents good is context engineering.

### Optimization Priorities

So, we're going to optimize for:

- Correctness
- Completeness
- Size
- Trajectory

I'm not going to talk about a lot about trajectory because it's very vibes based right now.

But to invert that, the worst thing to have in your context window is:

1. Bad info
2. Second worst thing is missing info
3. And then just too much noise

And if you wanted an equation, we made this dumb equation.

---

## The 170K Token Budget

Jeff figured this out. Well, Jeff, lots of people are figuring this out, but Jeff Huntley works on source AMP. Which I know Bang was supposed to be speaking tonight. I'm sure I hope he will appreciate this talk. In the spirit of what they've been talking about, you got about 170,000 tokens. The less of them you use to do the work, the better results you will get.

He wrote this thing called Ralph Wigum as a software engineer. And he talks about, hey, this is the dumbest way to use coding agents and it works really, really well, which is just to run a same prompt in a loop overnight for 12 hours while he's asleep in Australia and put it on a live stream. I actually think that he's being humble. It's a very, very smart way to use coding agents if you understand LMS and context windows.

I'll link that article as well. I'll put up a QR code at the end with everything.

---

## Sub-Agents for Inline Compaction

The next step is you can do inline compaction with sub aents. A lot of people saw cloud code sub aents and they jumped in and they said, "Okay, cool. I'm going to have my product manager and my data scientist and my front-end engineer and like maybe that works."

But they're really about context control.

And so a really common task that people use sub agents for when they're doing this kind of like high level coding agents is they will find you want to find where something happens. You want to understand how information flows across multiple components in a codebase.

You will say maybe you'll steer it to use a sub agent. A lot of models have in their system prompts to use a sub aent automatically and you say hey go find where this happens and then the parent model will call a tool that says go give this message to a sub aent. the sub agent goes and finds where the file is, returns it to the parent agent. The parent agent can get right to work without having to have the context burden of all of that reading and searching.

### The Ideal Sub-Agent Response

And the ideal sub agent response looks something like this. And I'm not going to talk about how we made this or where it comes from yet.

There's a lot to be said about sub agents. The challenge of like playing telephone and like you care about the thing that comes back from the sub agent. So, how do you prompt the parent model to prompt the child model about how it should return its information?

If you've ever seen this thing, we're doing basically what is it? Stochastic system. This is a deterministic system and it gets chaotic. Imagine with nondeterministic systems.

---

## Frequent Intentional Compaction

So what works even better than sub agents and the thing that we're doing every day now is what I call frequent intentional compaction. Building your entire development workflow around context management.

So our goal all the time is to keep context utilization under 40%.

### The Three Phases

And we have three phases:

1. **Research**
2. **Plan**
3. **Implement**

### Phase 1: Research

The research is really like understand how the system works and all the files that matter and perhaps like where a problem is located.

This is our research prompt. It's really long. It's open source. You can go find it.

This is the output of our research prompt. It's got file names and line numbers so that the agent reading this research knows exactly where to look. It doesn't have to go search 100 files to figure out how things work.

### Phase 2: Planning

The planning step is really just like tell me every single change you're going to make. not line by line, but like include the files and the snippets of what you're going to change and be very explicit about how we're going to test and verify at every step.

So, this is our planning prompt. This is one of our plans.

### Phase 3: Implement

And then we implement and we go write the code. And honestly, if the plan is good, I'm never shouting at cloud cloud anymore. And if I'm shouting at cloud, it's because the plan was bad. And the plan is always much shorter than the code changes sometimes, most of the time.

And as you're implementing, we keep the context under 40%. So, we constantly update the plan. We say, "This is done. On to the next phase. is new context window.

This is our implement prompt. These are all open source. I'll tell you where to find them. This is not magic. You have to read this It will not work.

### Human Review Steps

And so we build it around intentional human review steps because a research file is a lot easier to read than a 2000 line PR. But you can stop problems early. This is our linear workflow for how we move this stuff through the process.

---

## What is Code Review For?

And I want to stop. Does anyone know what code review is for?

anybody? Yeah, me neither.

Code review is about a lot of things, but the most important part is mental alignment. Keeping the people on the team aware of how the system is changing and why as it evolves over time.

I can't read 2,000 lines of golining every day, but I can sure as heck read 200 lines of an implementation plan. And if the plans are good, that's enough because we can catch problems early and we can maintain shared understanding of what's happening in our code.

---

## Case Studies

So putting this into practice, I do a podcast with another YC founder named Vibbov. He built Bam. I don't know, has anyone here you used BAML before? All right, we got a couple BAML guys.

### Case Study 1: BAML (300,000 Line Rust Codebase)

I decided, I didn't tell Vibb I was doing this. We decided to see if we could oneshot a fix to a 300,000 line RS codebase.

And the episode is 75 minutes and we go through the whole process of all the things that we tried and what worked and what didn't work and what we learned. I'm not going to go into it. I'll give you a link.

But we did get it merged. The PR was so good the CTO did not know I was doing it as a bit and he had merged it by the time we were recording the episode.

So confirmed works in brownfield code bases and no slop. It got merged.

### Case Study 2: Boundary (35,000 Lines in 7 Hours)

And I wanted to see if it could solve a complex problem. So I sat down with the boundary CEO and for 7 hours we sat down and we shipped 35,000 lines of code. A little bit of it was generated but we wrote a lot of code that day and he estimated that was 1 to two weeks of work roughly.

So it can solve complex problems. You can add WASM support to a programming language.

---

## The Key Insight

And so the biggest insight from here that I would ask you to take away is that:

- A bad line of code is a bad line of code
- A bad part of a plan can be hundreds of bad lines of code
- A bad line of research, a misunderstanding of how the system works and how data flows and where things happen can be thousands of bad lines of code

And so you have this hierarchy of where do you spend your time? And yes, the code is important and it has to be correct. But you can get a lot more for your time by focusing on specifying the right problem and what you want and by understanding making sure that when you launch the coding agent, it knows how the system works.

And of course, our cloud MD and our slash commands are like we basically like test those for weeks before anyone's allowed to change them. Um, so we review the re research and plans and we have mental alignment.

---

## Results

I don't have time to talk about this one because I think I'm already over. But how did we do?

We we did the goals. I didn't I didn't ask for these goals, but they were thrust upon me and we solved them.

We spent a whole lot of tokens. This is a team of three in a month. These are credits, by the way.

But I don't think we're going I I don't think we're switching to the max plan because this is working well enough that I'm it's I mean, it's worth it's worth spending because it saves us a lot of time as engineers.

Our intern Sam is here somewhere. He shipped two PRs on his first day. on his eighth day, he shipped like 10 in a day. This works.

We did the BAML thing. And again, I I don't I don't look at code anymore. I just read specs.

---

## What's Next?

So, what's next? I kind of maybe think coding agents are going to get a little bit commoditized, but the team and the workflow transformation will be the hard part.

Getting your team to embrace new ways of communicating and structuring how you work is going to be really, really hard and uncomfortable for a lot of teams. People are figuring this out. you should try to figure this out because otherwise you're gonna have a bad time.

We're trying to help people figure this out. We're working with everybody from six person YC startups to a thousand people public companies.

There is a Oh, we're doing an event tomorrow on hyperengineering. It is very very close to capacity, but if you come find me after this and give me a good pitch, there are a couple spots left.

And there's a link to the video where we talk about this for 90 minutes and me and Vibb bust each other's balls for a while.

---

That is advanced context engineering for coding agents. Thank you.

*[Music]*
