## Objective 

This app backend uses several crewai agents to recommend the best open source HugginFace LLM models - according to users hardware configuration.

The fronted should use a web-browser page to gather all the inputs and give back the result output.


## Inputs

All inputs will be for:

### Hardware & OS 
- GPU
- CPU
- RAM
- hard disk memory
- opearation system

### LLM model type or usage: chat, coding, image generation, etc.

## Outputs: the Top 5 recommended HugginFace LLM models will be outputed on the results page in a nice format with simple explanations for their pros and cons (according to the hardware specs)

## Workflow

### CrewAI Agents

All present agents @agents.yaml file should be deleted and replaced with new ones:

- Hardware Agent: gathers all the hardware specs
- HugginFace Specialist: looks for best LLM models that will work on that hardware and picks 10
- Judge: Decides which are the top 5 models and provides pros and cons.

### Frontend

Streamlit is the recommended platform for the first UI iteration because it keeps everything in Python, lets us build validated forms quickly, and deploys easily to HuggingFace Spaces alongside the referenced models. See `docs/frontend_proposal.md` for the detailed comparison against Gradio and React.
