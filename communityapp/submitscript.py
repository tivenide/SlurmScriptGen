import os
import yaml
import streamlit as st

st.set_page_config(
    page_title="submitscript", page_icon=":large_blue_circle:", layout="wide"
)

st.header(
    " Welcome to slurm script generator",
    help="This is a simple web application that generates slurm submit scripts based on our infrastructure's naming conventions and workflow. It helps users quickly create job submission scripts without having to manually format the script each time. The app ensures that the generated scripts adhere to our organization's standards, making the job submission process more efficient and consistent.",
    divider="rainbow",
)
col_a, col_b = st.columns(2)
with col_a:
    with st.container():
        st.write("#### general information")
        col_1, col_2 = st.columns(2)
        image_name = col_1.text_input("image name")
        image_tag = (
            col_2.text_input(
                "image tag", placeholder="latest", help="default: *latest*"
            )
            or "latest"
        )
        col_1, col_2 = st.columns(2)
        col_1.write(
            f"**{image_name}\:{image_tag}**"
        )
        col_2.write(
            f"**{image_name}_{image_tag}.sif**"
        )
        col_1, col_2 = st.columns(2)
        partition_name = col_1.text_input("partition name")
        registry_name = col_2.text_input("registry name")

    apptainer_pull = st.toggle("apptainer pull")

    st.write("#### resources config")
    with st.container():
        try:
            with open("static/res_conf.yml", "r") as file:
                res_conf = yaml.load(file, Loader=yaml.FullLoader)
        except FileNotFoundError:
            res_conf = {"slim": {"cpu": 1, "mem": 1}}

        option = st.selectbox(
            "default configs",
            list(res_conf.keys()),
            index=None,
            placeholder="Select a default config...",
            help="Select a default configuration for the CPU and memory resources to be pre-filled in the submission script. These values should be further customized as needed for your specific job requirements.",
        )

        res_conf_cpu = res_conf[f"{option}"]["cpu"] if option else 1
        res_conf_mem = res_conf[f"{option}"]["mem"] if option else 1

        col_1, col_2, col_3 = st.columns(3)
        resources_nodes = (
            col_1.number_input(
                "nodes",
                min_value=1,
                step=1,
                help="The number of compute nodes to allocate for your job. Setting this to 1 is suitable for tasks that do not require distributed computing resources. For jobs that can benefit from parallelization across multiple nodes, you can increase this value accordingly. **Unless you have a specific reason to change this setting, it's generally best to leave it at 1.**",
            )
            or 1
        )
        resources_cpu = (
            col_2.number_input(
                "cpu (per task)",
                min_value=1,
                step=1,
                value=res_conf_cpu,
                help="The number of CPU cores to allocate for each task in your job. This setting ensures that your tasks have access to the required computational resources to run efficiently, but will only result in faster computation if your code is able to take advantage of multiple cores.",
            )
            or 1
        )
        resources_mem = (
            col_3.number_input(
                "ram in GB",
                min_value=1,
                step=1,
                value=res_conf_mem,
                help="The amount of memory (in gigabytes) to allocate for each task in your job. This setting ensures that your tasks have access to the required memory resources to run effectively, but you should ensure that your code can efficiently utilize the allocated memory.",
            )
            or 1
        )

        gpu_support = st.toggle(
            "GPU support", help="Only use this if your code actually utilizes GPUs."
        )
        job_array_support = st.toggle(
            "job array support",
            help="Job arrays allow you to submit multiple similar tasks as a single job, with each task identified by a unique task ID (e.g., ${SLURM_ARRAY_TASK_ID}). This can greatly simplify the management and execution of parallel or parametric studies.",
        )
        if job_array_support:
            col_1, col_2, col_3 = st.columns(3)
            slurm_array_task_min = (
                col_1.number_input("SLURM_ARRAY_TASK_MIN", min_value=0, step=1) or 0
            )
            slurm_array_task_max = (
                col_2.number_input("SLURM_ARRAY_TASK_MAX", min_value=1, step=1) or 1
            )
            slurm_array_task_simultaneously = (
                col_3.number_input("simultaneously", min_value=1, step=1) or 1
            )
            if slurm_array_task_min >= slurm_array_task_max:
                st.warning(
                    "Caution: SLURM_ARRAY_TASK_MIN >= SLURM_ARRAY_TASK_MAX", icon="⚠️"
                )
            st.info("directory *out/* must be defined")
        st.write("###### job duration")
        col_1, col_2 = st.columns(2)
        resources_time_hours = col_1.number_input(
            "hours", min_value=0, max_value=48, step=1, value=2
        )
        resources_time_minutes = col_2.number_input(
            "minutes", min_value=0, max_value=59, step=1, value=0
        )

    st.write("#### container config")
    with st.container():
        path_workdir = st.text_input(
            "path of working directory within container", placeholder="/IntroContCudaML"
        )
        start_command = st.text_input(
            "starting command", placeholder="python3 src/main.py"
        )
        st.write("###### mount paths")
        path_outside_cont = st.text_input(
            "path outside the container", placeholder="~/projects/intro/data"
        )
        path_inside_cont = st.text_input(
            "path inside the container", placeholder="/IntroContCudaML/data"
        )

# script generation
default_partition = partition_name # os.getenv("DEFAULT_PARTITION")
local_registry = registry_name # os.getenv("LOCAL_REGISTRY")

text_pull = f"""echo 'pull image + convert to sif'
apptainer pull docker://{local_registry}/{image_name}:{image_tag}
echo 'pull and convert finished'
"""

text_content_list = []
text_content_list.append("#!/bin/bash")
text_content_list.append(
    f"#SBATCH --job-name='{image_name}_{image_tag}'"
)
text_content_list.append(f"#SBATCH --partition={default_partition}")
text_content_list.append("#SBATCH --output=job.out")
text_content_list.append("#SBATCH --error=job.err")
text_content_list.append(f"#SBATCH --nodes={resources_nodes}")
text_content_list.append(f"#SBATCH --cpus-per-task={resources_cpu}")
text_content_list.append(f"#SBATCH --mem={resources_mem}G")
if gpu_support:
    text_content_list.append("#SBATCH --gres=gpu:1")
if job_array_support:
    text_content_list.append(
        f"#SBATCH --array={slurm_array_task_min}-{slurm_array_task_max}%{slurm_array_task_simultaneously}"
    )
text_content_list.append(
    f"#SBATCH -t 0-{resources_time_hours:02d}:{resources_time_minutes:02d}:00   # time in d-hh:mm:ss"
)

if apptainer_pull:
    text_content_list.append(text_pull)

text_content_list.append("echo 'run container'")
if job_array_support:
    text_content_list.append("srun -o out/${SLURM_ARRAY_TASK_ID}.out \\")
    text_content_list.append(" apptainer exec \\")
else:
    text_content_list.append("apptainer exec \\")

if gpu_support:
    text_content_list.append(" --nv \\")

if path_outside_cont and path_inside_cont:
    text_content_list.append(f" --bind {path_outside_cont}:{path_inside_cont} \\")
elif (path_outside_cont and not path_inside_cont) or (
    not path_outside_cont and path_inside_cont
):
    st.warning("Caution: Both paths must be provided.", icon="⚠️")
else:
    pass

if path_workdir:
    text_content_list.append(f" --pwd {path_workdir} \\")

text_content_list.append(
    f" {image_name}_{image_tag}.sif \\"
)

if start_command:
    text_content_list.append(f" {start_command}")

text_content_list.append("echo 'container finished'")
text_content_list.append("# end of job script")
text_content = "\n".join(text_content_list)


with col_b:
    st.write("#### submit script")
    st.code(text_content, language="bash")
    filename = st.text_input(
        "filename for submit script", value="my_submitscript.sbatch"
    )
    filename = filename.strip().replace(" ", "")
    if not filename:
        filename = "my_submitscript.sbatch"
    st.download_button("download submit script", data=text_content, file_name=filename)
    st.write("submit the script on a head node with:")
    st.code(f"sbatch {filename}")

st.divider()
st.write("Thank you for using the generator. Copyright tivenide. All rights reserved.")
