import os
import subprocess
import uuid
import logging

from utils import KICAD_FULL_IMAGE_ID

kicad_img_home_path ="/home/kicad"

'''
        String[] firstCmd = { "docker", "run", "-v", kicad_project_dir + ":" + mounted_prj_path,
                KICAD_IMAGE_ID, "kicad-cli", "sch",
                "export", "netlist", "--format", "allegro",
                mouted_sch_root_path, "-o",
                mounted_prj_path + "/" + output_file_name
        };


'''
#
def export_net_list(root_sch_file_name):
    kicad_project_dir = os.path.dirname(root_sch_file_name)
    pcb_name = os.path.basename(root_sch_file_name)
    mounted_prj_path = os.path.join(kicad_img_home_path, str(uuid.uuid4())).replace("\\", "/")
    mounted_pcb_fp = os.path.join(mounted_prj_path, pcb_name).replace("\\", "/")
    output_file_name = str(uuid.uuid4()) + ".txt"
    # docker_output_fn = os.path.join(mounted_prj_path, output_file_name).replace("\\", "/")

    first_cmd = [
        "docker", "run", "--rm",
        "-v", f"{kicad_project_dir}:{mounted_prj_path}",
        KICAD_FULL_IMAGE_ID,
        "kicad-cli", "sch",
        "export", "netlist", "--format", "kicadxml",
        mounted_pcb_fp, "-o",
        f"{mounted_prj_path}/{output_file_name}"
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

    # c_output_file_name = str(uuid.uuid4()) + ".glb"
    # c_docker_output_fn = os.path.join(mounted_prj_path, c_output_file_name).replace("\\", "/")

    # second_cmd = ["docker", "run", "-v", f"{kicad_project_dir}:{mounted_prj_path}",
    #               KICAD_IMAGE_ID, "npx", "gltfpack",
    #               "-i",
    #               docker_output_fn, "-v", "-cc", "-tc", "-ts", "0.5", "-o",
    #               c_docker_output_fn
    #               ]

    # print(" ".join(second_cmd))

    # try:
    #     process_pack = subprocess.Popen(second_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #     _, stderr = process_pack.communicate()
    #     if stderr:
    #         logging.error(stderr.decode())
    # except Exception as e:
    #     logging.error(e)

    # try:
    #     process_pack.wait()
    # except Exception as e:
    #     logging.error(e)

    # return os.path.join(kicad_project_dir, c_output_file_name).replace("\\", "/")


def main():
    import time

    export_net_list(r"D:/code/kicad-cli-python/pal-ntsc.kicad_sch")



if __name__ == "__main__":
    main()
