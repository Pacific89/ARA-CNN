import argparse
import numpy as np
import os
import csv

from keras.models import load_model
from keras.preprocessing.image import load_img, img_to_array

from variational_dropout import build_variational_model, build_variational_inference_function, compute_table_uncertainty
from model_utils import import_folder_to_numpy_array, single_class_accuracy
from config import CLASS_DICT, IMAGE_SIZE


VARIATIONAL_SAMPLES = 50
TEST_RUNS = 10


class ModelLoader(object):
    def __init__(self, model_path):
        self.model_path = model_path
        self.trained_model = None

    def load_model(self):
        self.trained_model = load_model(self.model_path,
                                        custom_objects={'fn': single_class_accuracy(0)})
        self.trained_model.summary()

    def test_folder_variational(self, test_set_path, measure, max_img_count=5000):
        import os
        variational_inference_model = build_variational_model(
            dropout_model_instance=self.trained_model, )
        variational_inference_function = build_variational_inference_function(
            variational_inference_model=variational_inference_model, )

        images = None
        counter = 0

        for img in os.listdir(test_set_path):
            if counter >= max_img_count:
                break

            test_img = img_to_array(
                load_img(path=os.path.join(test_set_path, img), grayscale=False, target_size=IMAGE_SIZE))
            test_img = test_img[None, ...]

            vectr = np.vectorize(lambda x: x / 255.0)
            mapped_test_img = vectr(test_img)
            if images is None:
                images = mapped_test_img
            else:
                images = np.append(images, np.array(mapped_test_img), axis=0)
            counter += 1

        all_p = []
        all_u = []

        for i in range(0, TEST_RUNS):
            test = variational_inference_function(images, VARIATIONAL_SAMPLES)
            uncertainties = compute_table_uncertainty(test, measure)
            predictions = list(test.mean(axis=0))
            all_u.append(uncertainties)
            all_p.append(predictions)

        img_results = [[0 for x in range(0, len(CLASS_DICT.keys()))] for i in range(0, len(images))]
        uncertainty_results = [0 for i in range(0, len(images))]

        for i in range(0, len(images)):
            for run in all_u:
                uncertainty_results[i] += run[i]

            for run in all_p:
                img_result = run[i]
                for j in range(0, len(CLASS_DICT.keys())):
                    img_results[i][j] += img_result[j]

        for i in range(0, len(images)):
            uncertainty_results[i] /= TEST_RUNS

            for j in range(0, len(CLASS_DICT.keys())):
                img_results[i][j] /= TEST_RUNS

        return zip(os.listdir(test_set_path), img_results, uncertainty_results)

    def get_normalizer(self):
        import staintools

        target_img_path = "/usr/local/src/Images/MUS-AAEKNQNW.tif"
        target_img = staintools.read_image(target_img_path)
        normalizer = staintools.StainNormalizer(method="macenko")
        normalizer.fit(target_img)

        return normalizer
    def test_coords_variational(self, test_img_path, coord_file, measure, max_img_count=1000, normalize=True):
        import os
        import h5py
        import openslide
        import time

        variational_inference_model = build_variational_model(
            dropout_model_instance=self.trained_model, )
        variational_inference_function = build_variational_inference_function(
            variational_inference_model=variational_inference_model, )

        images = None
        counter = 0

        if normalize:
            normalizer = self.get_normalizer()
        # img_files = [f for f in os.listdir(test_set_path) if f.endswith("svs")]
        # coord_files = [f.replace("svs", "h5") for f in img_files]

        img_file = test_img_path

        print(img_file, coord_file)
        with h5py.File(os.path.join(coord_file), "r") as f:
            patch_coords = np.array(f["coords"])
        print(len(patch_coords))

        patch_level = 0
        patch_size = 128
        wsi = openslide.open_slide(os.path.join(img_file))
        patch_ids = []
        p_coords = []
        all_img_results = []
        all_un_results = []
        t = time.time()
        for coords in patch_coords:
            # if counter >= max_img_count:
            #     break
            images = None
            test_img = img_to_array(wsi.read_region(coords, patch_level, tuple([patch_size, patch_size])).convert('RGB'))
            if normalize:
                try:
                    test_img = normalizer.transform(np.uint8(test_img))
                except Exception:
                    print("Warning: ", Exception)
                    pass
            print(" {0} / {1} | Time: {2}".format(counter, len(patch_coords), time.time()-t))
            t = time.time()
            # test_img = img_to_array(
            #     load_img(path=os.path.join(test_set_path, img), grayscale=False, target_size=IMAGE_SIZE))

            test_img = test_img[None, ...]

            vectr = np.vectorize(lambda x: x / 255.0)
            mapped_test_img = vectr(test_img)
            if images is None:
                images = mapped_test_img
            # else:
            #     images = np.append(images, np.array(mapped_test_img), axis=0)

            all_p = []
            all_u = []

            for i in range(0, TEST_RUNS):
                test = variational_inference_function(images, VARIATIONAL_SAMPLES)
                uncertainties = compute_table_uncertainty(test, measure)
                predictions = list(test.mean(axis=0))
                all_u.append(uncertainties)
                all_p.append(predictions)

            img_results = [[0 for x in range(0, len(CLASS_DICT.keys()))] for i in range(0, len(images))]
            uncertainty_results = [0 for i in range(0, len(images))]

            for i in range(0, len(images)):
                for run in all_u:
                    uncertainty_results[i] += run[i]

                for run in all_p:
                    img_result = run[i]
                    for j in range(0, len(CLASS_DICT.keys())):
                        img_results[i][j] += img_result[j]

            for i in range(0, len(images)):
                uncertainty_results[i] /= TEST_RUNS

                for j in range(0, len(CLASS_DICT.keys())):
                    img_results[i][j] /= TEST_RUNS

            patch_ids.append(img_file + "_num_" + str(counter))
            p_coords.append(coords)
            all_img_results.append(img_results)
            all_un_results.append(uncertainty_results)
            counter += 1

        return zip(patch_ids, all_img_results, all_un_results, p_coords)
        


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model-path', dest='model_path', help='Path to the model file')
    parser.add_argument('--input-images', dest='input_images', help='Path to the folder with images to test')
    parser.add_argument('--measure', dest='measure', help='Uncertainty measure', choices=['Entropy', 'BALD'])
    parser.add_argument('--output-path', dest='output_path', help='Output folder for the results file')
    parser.add_argument('--coords', dest='coords', help='input hdf5 that containes coordinates', default=False, required=False, type=str)

    args = parser.parse_args()

    model_loader = ModelLoader(args.model_path)
    model_loader.load_model()

    if args.coords:
        result = model_loader.test_coords_variational(args.input_images, args.coords, args.measure)
    else:
        result = model_loader.test_folder_variational(args.input_images, args.measure)

    if not os.path.exists(args.output_path):
        os.mkdir(args.output_path)

    with open(os.path.join(args.output_path, 'results.csv'), 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['image_name', 'uncertainty'] + list(CLASS_DICT.keys()) + ['patch_x', 'patch_y'])
        for img, pred, unc, p_coords in result:
            print(img, pred, unc, p_coords)
            writer.writerow([img, unc[0]] + pred[0] + [p_coords[0], p_coords[1]])
        pass