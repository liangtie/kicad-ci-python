import os
import subprocess
import uuid
import logging

kicad_img_id = "a37c2763212f"
kicad_img_home_path ="/home/kicad"

def export_glb(root_sch_file_name):
    kicad_project_dir = os.path.dirname(root_sch_file_name)
    pcb_name = os.path.basename(root_sch_file_name)
    mounted_prj_path = os.path.join(kicad_img_home_path, str(uuid.uuid4())).replace("\\", "/")
    mouted_pcb_fp = os.path.join(mounted_prj_path, pcb_name).replace("\\", "/")
    output_file_name = str(uuid.uuid4()) + ".glb"
    docker_output_fn = os.path.join(mounted_prj_path, output_file_name).replace("\\", "/")

    first_cmd = ["docker", "run",
                 "-v", f"{kicad_project_dir}:{mounted_prj_path}",
                 kicad_img_id, "kicad-cli", "pcb",
                 "export", "glb", "--subst-models", "--include-tracks",
                 mouted_pcb_fp, "-o",
                 docker_output_fn
                 ]
    print(" ".join(first_cmd))

    try:
        process_export = subprocess.Popen(first_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _, stderr = process_export.communicate()
        if stderr:
            logging.error(stderr.decode())
    except Exception as e:
        logging.error(e)

    try:
        process_export.wait()
    except Exception as e:
        logging.error(e)

    c_output_file_name = str(uuid.uuid4()) + ".glb"
    c_docker_output_fn = os.path.join(mounted_prj_path, c_output_file_name).replace("\\", "/")

    second_cmd = ["docker", "run", "-v", f"{kicad_project_dir}:{mounted_prj_path}",
                  kicad_img_id, "npx", "gltfpack",
                  "-i",
                  docker_output_fn, "-v", "-cc", "-tc", "-ts", "0.5", "-o",
                  c_docker_output_fn
                  ]

    print(" ".join(second_cmd))

    try:
        process_pack = subprocess.Popen(second_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _, stderr = process_pack.communicate()
        if stderr:
            logging.error(stderr.decode())
    except Exception as e:
        logging.error(e)

    try:
        process_pack.wait()
    except Exception as e:
        logging.error(e)

    return os.path.join(kicad_project_dir, c_output_file_name).replace("\\", "/")


# def main():
#     import time

#     start_time = time.time()

#     unziped_prj_path = "/home/hq/kicad/complex_hierarchy"  # NOTE: Project folder needs to have write permission
#     pcb_fn = "video.kicad_pcb"
#     net_list = export_glb(os.path.join(unziped_prj_path, pcb_fn))

#     end_time = time.time()
#     execution_time = (end_time - start_time) * 1000  # Convert to milliseconds

#     print(f"程序执行时间: {execution_time} 毫秒")


# if __name__ == "__main__":
#     main()
