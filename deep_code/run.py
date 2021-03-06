# Put train, eval and test here
import sys
from time import time
import yaml
import utils
import malconv_model
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from exe_dataset import ExeDataset, ExeDatasetNoLabels
from sklearn.metrics import confusion_matrix
import numpy as np


def test_model(config_file, model, device):
    """
    :param config_file: (string) path to a '.yaml' configuration file.
    :param model: (MalConv).
    :param device: the device that was used for the model.
    """
    # load configurations
    try:
        conf = yaml.load(open(config_file, 'r'))
    except:
        print('Error with test configuration yaml')
        sys.exit()

    classes = utils.read_lines(conf[LABELS])
    i2l = {i: l for i, l in enumerate(classes)}
    l2i = {l: i for i, l in i2l.iteritems()}

    # create loader
    files = utils.read_lines(conf[FILES_LS_PATH])  # list files to predict on
    test_loader = DataLoader(ExeDatasetNoLabels(files, l2i, conf[NUM_BYTES]),
                             batch_size=1, shuffle=False, num_workers=conf[WORKERS])

    # predict
    with open(conf[TARGET_FILE], 'w') as f:
        for x in test_loader:  # todo check this
            if device is not None:
                x = x.to(device)
            pred = model(x)
            pred_label = torch.max(pred, 1)[1].item()
            f.write('{}\n'.format(pred_label))
        f.close()


def validate_dev_set(valid_loader, model, device, size_dev, conf=False):
    """
    check performance of model on dev-set.
    :param valid_loader: (DataLoader).
    :param model: (MalConv).
    :param device: the device used for the given model.
    :param size_dev: size of the dev set.
    :param conf: (boolean) show confusion matrix.
    :return: model accuracy on dev-set.
    """
    t0 = time()
    good = 0.0
    model.eval()

    if conf:
        golds, preds = [], []

    for val_batch_data in valid_loader:
        exe_input, labels = val_batch_data[0], val_batch_data[1]
        if device is not None:
            exe_input, labels = exe_input.to(device), labels.to(device)

        pred = model(exe_input)

        gold_label = labels.data
        pred_label = torch.max(pred, 1)[1].data
        if conf:
            golds.extend(gold_label)
            preds.extend(pred_label)
        # TODO check if this summing works
        good += (gold_label == pred_label).sum()

    acc = good / size_dev
    if conf:
        print confusion_matrix(golds, preds)
    return acc, time() - t0


def eval_on(config_file, model, device):
    """
    :param config_file: (string) path to a '.yaml' configuration file.
    :param model: (MalConv).
    :param device: the device that was used for the model.
    """
    try:
        conf = yaml.load(open(config_file, 'r'))
    except:
        print('Error with dev configuration yaml')
        sys.exit()

    classes = utils.read_lines(conf[LABELS])
    i2l = {i: l for i, l in enumerate(classes)}
    l2i = {l: i for i, l in i2l.iteritems()}

    path2label = utils.create_path2label_dict(conf[MAIN_DIR], conf[L2DIR])
    size_dev = len(path2label)
    keys = list(path2label.viewkeys())
    np.random.shuffle(keys)
    dev_set = [(key, path2label[key]) for key in keys]
    fps_dev, y_dev = utils.split_to_files_and_labels(dev_set)

    validloader = DataLoader(ExeDataset(fps_dev, y_dev, l2i, conf[NUM_BYTES]),
                             batch_size=conf[BATCH], shuffle=False, num_workers=conf[WORKERS])
    acc, t = validate_dev_set(validloader, model, device, size_dev, conf[CONF_MAT])
    print 'time-dev: {:.2f} dev-acc: {:.4f}'.format(t, acc)


def train_on(path2label, labels_filepath, first_n_byte=2000000, lr=0.001, num_epochs=3, save=None,
             batch_size=32, num_workers=10, show_matrix=False):
    """
    :param path2label: (dict) maps file-path to its label.
    :param labels_filepath: (string) path to a file, each line in it is a label in the dataset.
    :param first_n_byte: (int) number of bytes to read from each file.
    :param lr: (float) learning rate.
    :param num_epochs: (int) number of epochs.
    :param save: None for no saving,
                 else string, path to the file to be created, where the model will be saved.
    :param batch_size: (int) size of batch for train and dev data-loaders.
    :param num_workers: (int) number of workers for train and dev data-loaders.
    :param show_matrix: (boolean) show confusion matrix.
    :return: device that was used for the model.
    """
    classes = utils.read_lines(labels_filepath)

    # create model
    model = malconv_model.MalConv(classes, first_n_byte)
    device = utils.model_to_cuda(model)

    i2l = {i: l for i, l in enumerate(classes)}
    l2i = {l: i for i, l in i2l.iteritems()}

    # load data
    train_set, dev_set = utils.split_data_set(path2label)
    fps_train, y_train = utils.split_to_files_and_labels(train_set)
    fps_dev, y_dev = utils.split_to_files_and_labels(dev_set)

    # transfer data to DataLoader object
    dataloader = DataLoader(ExeDataset(fps_train, y_train, l2i, first_n_byte),
                            batch_size=batch_size, shuffle=True, num_workers=num_workers)
    validloader = DataLoader(ExeDataset(fps_dev, y_dev, l2i, first_n_byte),
                             batch_size=batch_size, shuffle=False, num_workers=num_workers)

    if len(classes) == 2:
        criterion = nn.BCEWithLogitsLoss()
    else:
        criterion = nn.CrossEntropyLoss()
    adam_optim = torch.optim.Adam(model.parameters(), lr)

    total_loss = 0.0
    total_step = 0

    for epoch in range(num_epochs):
        t0 = time()
        good = 0.0
        model.train()

        for batch_data in dataloader:
            adam_optim.zero_grad()

            exe_input, label = batch_data[0], batch_data[1]
            if device is not None:
                exe_input, label = exe_input.to(device), label.to(device)
            pred = model(exe_input)

            loss = criterion(pred, label)
            total_loss += loss
            loss.backward()
            adam_optim.step()

            gold_label = label.data
            # TODO check if this way of summing works
            pred_label = torch.max(pred, 1)[1].data
            good += (gold_label == pred_label).sum()

            total_step += 1
        acc_train = good / len(y_train)
        avg_loss_train = total_loss / len(y_train)
        acc_dev, time_dev = validate_dev_set(validloader, model, device, len(y_dev))
        print('{} train-time: {:.2f} train-acc: {:.4f} train-loss: {:.5f} dev-time: {:.2f} dev-acc: {:.4f}'.format(
            epoch, time() - t0, acc_train, avg_loss_train, time_dev, acc_dev
        ))
        # TODO CHECK IF TO ADD LOG
        # log.write('{:.4f},{:.5f},{:.4f}\n'.format(acc_train, avg_loss_train, acc_dev))

    # conf matrix
    acc_dev, time_dev = validate_dev_set(validloader, model, device, len(y_dev), conf=show_matrix)
    print('dev-time: {:.2f} dev-acc: {:.4f}'.format(time_dev, acc_dev))
    if save:
        torch.save(model, save)
    return device


# arguments to main
TRAIN = '-train'
SAVE = '-save'
LOAD = '-load'
EVAL = '-eval'
TEST = '-test'

# keys for .yaml files
MAIN_DIR = 'main_dir'
NUM_BYTES = 'first_n_byte'
LR = 'lr'
EPOCHS = 'num_epochs'
LABELS = 'labels'
L2DIR = 'labels2dir'
BATCH = 'batch'
WORKERS = 'workers'
CONF_MAT = 'conf_mat'
FILES_LS_PATH = 'files_ls_path'
TARGET_FILE = 'target_file'


def main():
    """
    Args - can combine multiple:
        [-train configuration_file]
        [-save model_filename]
        [-load model_filename]
        [-eval configuration_file]
        [-test configuration_file]
    """
    args = sys.argv[1:]

    if TRAIN in args:
        config_file = args[args.index(TRAIN) + 1]
        try:
            conf = yaml.load(open(config_file, 'r'))
        except:
            print('Error with train configuration yaml')
            sys.exit()
        target_file = None
        if SAVE in args:
            target_file = args[args.index(SAVE) + 1]
        path2label = utils.create_path2label_dict(conf[MAIN_DIR], conf[L2DIR])
        device = train_on(path2label, conf[LABELS], conf[NUM_BYTES], conf[LR], conf[EPOCHS], target_file,
                          conf[BATCH], conf[WORKERS], conf[CONF_MAT])

    if LOAD in args:
        params_file = args[args.index(LOAD) + 1]
        model = torch.load(params_file)
        device = utils.model_to_cuda(model)

    if EVAL in args:
        config_file = args[args.index(EVAL) + 1]
        eval_on(config_file, model, device)

    if TEST in args:
        config_file = args[args.index(TEST) + 1]
        test_model(config_file, model, device)


if __name__ == '__main__':
    main()
