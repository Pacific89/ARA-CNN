# coding=utf-8
import json
import sys
import os
import argparse
import glob

# open config file for "RUN-COMMAND"
with open("/usr/local/config/ara_command_config.json") as json_file:
    ara_config = json.loads(json_file.read())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('input_pattern',
                help="one input file: example.svs",
                nargs="*")
    parser.add_argument('-c', '--config', help="json string with config parameters: \n Defaults: {0}".format(ara_config), default="config_light", type=str)

    args = parser.parse_args()

    if args.config:
        # try to read dict from json string and update default values
        try:
            config_dict = json.loads(args.config)
            ara_config.update(config_dict)
        except:
            print("Not a valid json config string. Using default")

    # get filename from command line arguments:
    try:
        input_folder = sys.argv[1]
    except:
        print("Please Provide a file")
        sys.exit()
    # create input path:
    input_path = glob.glob("/usr/local/data/{0}/*.svs".format(input_folder))[0]

    output_path = ara_config["output_path"] + "/{0}/data/clam".format(input_folder) # set output folder
    model_path = ara_config["model_path"] # choose config file
    measure = ara_config["measure"] # default in qc_pipeline: "" (empty string)
    coords = json.loads(ara_config["coords"].lower()) # force overwrite existing output files: default in qc_pipeline: False


    # create correct command to start HQC:
    command_hqc = "python /usr/local/src/src/test_model.py --input-images {0} --output-path {1} --model-path {2} --measure {3} --coords {4}".format(input_path, output_path, model_path, measure, coords)
    print(command_hqc)
    # start HQC:
    os.system(command_hqc)