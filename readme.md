# slurm script generator

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/streamlit/roadmap)

This is a simple web application that generates slurm submit scripts based on our infrastructure's naming conventions and workflow. It helps users quickly create job submission scripts without having to manually format the script each time. The app ensures that the generated scripts adhere to our organization's standards, making the job submission process more efficient and consistent.
## Features
- Intuitive web interface for easy script generation
- Automatic formatting based on our infrastructure's naming conventions
- Supports common slurm directives and options
- Customizable templates to match our organization's requirements
- Shareable generated scripts for collaboration and reuse

## Getting Started

Follow these steps to get started with slurm script generator:

1. Create an `.env-File` with the following variables that will be used for docker-compose:
```env
LOCAL_REGISTRY=my-registry.domain.com:<port>
DEFAULT_PARTITION=my-default-partition
```

2. Build and start the container via docker-compose
```commandline
docker compose up
```

3. Open your web browser to access the app.
```
Local URL:      http://localhost:8501
Network URL:    http://ip.of.your.server:8501
```
4. Fill out the form with the necessary details for your job submission, such as job name, resource requirements, and command to execute.

5. Copy the generated script and use it to submit your job to the slurm scheduler.

## Contributing

Contributions are welcome! Here's how you can set up the development environment:

1. Clone the repository:

```bash
git clone https://github.com/tivenide/SlurmScriptGen.git
cd SlurmScriptGen
```

2. Install the development requirements:

```bash
pip install -r requirements-dev.txt
```

3. Set up the pre-commit hooks:
```bash
pre-commit install
```

Thank you for your contribution!

## License

Copyright 2024 tivenide. All rights reserved.