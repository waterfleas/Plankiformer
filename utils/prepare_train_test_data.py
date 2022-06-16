###########
# IMPORTS #
###########

import pickle

import numpy as np
from joblib import dump
from sklearn.preprocessing import StandardScaler

from utils import create_data as cdata


class CreateDataset:
    def __init__(self, initMode='default', verbose=True):
        self.initMode = initMode
        self.fsummary = None
        self.tt = None
        self.verbose = verbose
        self.params = None
        self.paramsDict = None
        self.data = None
        self.trainSize = None
        self.testSize = None
        self.model = None
        self.opt = None

        return

    def LoadData(self, class_main):
        """
        Loads dataset using the function in the Cdata class.
        Acts differently in case it is the first time or not that the data is loaded

        The flag `training_data` is there because of how the taxonomists created the data directories. In the folders that I use for training there is an extra subfolder called `training_data`. This subfolder is absent, for example, in the validation directories.
        """

        # Default values
        datapaths = class_main.params.datapaths
        L = class_main.params.L
        class_select = class_main.params.class_select  # class_select==None has the explicit
        # meaning of selecting all the classes
        classifier = class_main.params.classifier
        compute_extrafeat = class_main.params.compute_extrafeat
        resize_images = class_main.params.resize_images
        balance_weight = class_main.params.balance_weight
        datakind = class_main.params.datakind
        training_data = class_main.params.training_data

        # Initialize or Load Data Structure
        if self.data is None:
            self.data = cdata.Cdata(datapaths, L, class_select, classifier, compute_extrafeat, resize_images,
                                    balance_weight, datakind, training_data=training_data)
        else:
            self.data.Load(datapaths, L, class_select, classifier, compute_extrafeat, resize_images, balance_weight,
                           datakind, training_data=training_data)

        # # Reset parameters
        # self.params.datapaths = self.data.datapath
        # self.params.L = self.data.L
        # self.params.class_select = self.data.class_select
        # self.params.datakind = self.data.kind
        # self.params.classifier = self.data.classifier
        # self.params.compute_extrafeat = self.data.compute_extrafeat
        # self.params.balance_weight = self.data.balance_weight
        return

    def CreateTrainTestSets(self, class_main, ttkind=None, classifier=None, save_data=None, balance_weight=None, testSplit=None,
                            valid_set=None, test_set=None, compute_extrafeat=None, random_state=12345):
        """
        Creates train and test sets using the CtrainTestSet class
        """

        # Set default value for ttkind
        if ttkind is None:
            ttkind = class_main.params.ttkind
        else:
            self.params.ttkind = ttkind

        # Set default value for testSplit
        if testSplit is None:
            testSplit = class_main.params.testSplit
        else:
            self.params.testSplit = testSplit

        if valid_set is None:
            valid_set = class_main.params.valid_set
        else:
            self.params.valid_set = valid_set

        if test_set is None:
            test_set = class_main.params.test_set
        else:
            self.params.test_set = test_set

        if classifier is None:
            classifier = class_main.params.classifier

        if save_data is None:
            save_data = class_main.params.save_data

        if balance_weight is None:
            balance_weight = class_main.params.balance_weight

        if compute_extrafeat is None:
            compute_extrafeat = class_main.params.compute_extrafeat

        self.tt = cdata.CTrainTestSet(self.data.X, self.data.y, self.data.filenames,
                                      ttkind=ttkind, classifier=classifier, balance_weight=balance_weight,
                                      testSplit=testSplit, valid_set=valid_set, test_set=test_set,
                                      compute_extrafeat=compute_extrafeat, random_state=random_state)

        # To save the data
        if class_main.params.ttkind == 'mixed':
            scaler = StandardScaler()
            scaler.fit(self.tt.trainXfeat)
            dump(scaler, class_main.params.outpath + '/Features_scaler_used_for_MLP.joblib')
            if class_main.params.test_set == 'yes':
                self.tt.trainXfeat = scaler.transform(self.tt.trainXfeat)
                self.tt.testXfeat = scaler.transform(self.tt.testXfeat)
                if class_main.params.valid_set == 'yes':
                    self.tt.valXfeat = scaler.transform(self.tt.valXfeat)
                    Data = [self.tt.trainFilenames, self.tt.trainXimage, self.tt.trainY,
                            self.tt.testFilenames, self.tt.testXimage, self.tt.testY,
                            self.tt.valFilenames, self.tt.valXimage, self.tt.valY,
                            self.tt.trainXfeat, self.tt.testXfeat, self.tt.valXfeat]
                elif class_main.params.valid_set == 'no':
                    Data = [self.tt.trainFilenames, self.tt.trainXimage, self.tt.trainY,
                            self.tt.testFilenames, self.tt.testXimage, self.tt.testY,
                            [], [], [],
                            self.tt.trainXfeat, self.tt.testXfeat, []]
            elif class_main.params.test_set == 'no':
                self.tt.trainXfeat = scaler.transform(self.tt.trainXfeat)
                Data = [self.tt.trainFilenames, self.tt.trainXimage, self.tt.trainY,
                        [], [], [],
                        [], [], [],
                        self.tt.trainXfeat, [], []]

        elif class_main.params.ttkind == 'feat':
            scaler = StandardScaler()
            scaler.fit(self.tt.trainX)
            dump(scaler, self.params.outpath + '/Features_scaler_used_for_MLP.joblib')
            if class_main.params.test_set == 'yes':
                self.tt.trainX = scaler.transform(self.tt.trainX)
                self.tt.testX = scaler.transform(self.tt.testX)
                if class_main.params.valid_set == 'yes':
                    self.tt.valXfeat = scaler.transform(self.tt.valXfeat)
                    Data = [self.tt.trainFilenames, [], self.tt.trainY,
                            self.tt.testFilenames, [], self.tt.testY,
                            self.tt.valFilenames, [], self.tt.valY,
                            self.tt.trainX, self.tt.testX, self.tt.valX]
                elif class_main.params.valid_set == 'no':
                    Data = [self.tt.trainFilenames, [], self.tt.trainY,
                            self.tt.testFilenames, [], self.tt.testY,
                            [], [], [],
                            self.tt.trainX, self.tt.testX, []]

            elif class_main.params.test_set == 'no':
                self.tt.trainX = scaler.transform(self.tt.trainX)
                Data = [self.tt.trainFilenames, [], self.tt.trainY,
                        [], [], [],
                        [], [], [],
                        self.tt.trainX, [], []]

        elif class_main.params.ttkind == 'image' and class_main.params.compute_extrafeat == 'no':
            if class_main.params.test_set == 'yes':
                if class_main.params.valid_set == 'yes':
                    Data = [self.tt.trainFilenames, self.tt.trainX, self.tt.trainY,
                            self.tt.testFilenames, self.tt.testX, self.tt.testY,
                            self.tt.valFilenames, self.tt.valX, self.tt.valY,
                            [], [], []]
                elif class_main.params.valid_set == 'no':
                    Data = [self.tt.trainFilenames, self.tt.trainX, self.tt.trainY,
                            self.tt.testFilenames, self.tt.testX, self.tt.testY,
                            [], [], [],
                            [], [], []]
            elif class_main.params.test_set == 'no':
                Data = [self.tt.trainFilenames, self.tt.trainX, self.tt.trainY,
                        [], [], [],
                        [], [], [],
                        [], [], []]

        elif class_main.params.ttkind == 'image' and class_main.params.compute_extrafeat == 'yes':
            scaler = StandardScaler()
            scaler.fit(self.tt.trainXfeat)
            dump(scaler, self.params.outpath + '/Aqua_Features_scaler_used_for_MLP.joblib')
            if class_main.params.test_set == 'yes':
                self.tt.trainXfeat = scaler.transform(self.tt.trainXfeat)
                self.tt.testXfeat = scaler.transform(self.tt.testXfeat)
                if self.params.valid_set == 'yes':
                    self.tt.valXfeat = scaler.transform(self.tt.valXfeat)

                    Data = [self.tt.trainFilenames, self.tt.trainXimage, self.tt.trainY,
                            self.tt.testFilenames, self.tt.testXimage, self.tt.testY,
                            self.tt.valFilenames, self.tt.valXimage, self.tt.valY,
                            self.tt.trainXfeat, self.tt.testXfeat, self.tt.valXfeat]
                elif class_main.params.valid_set == 'no':
                    Data = [self.tt.trainFilenames, self.tt.trainXimage, self.tt.trainY,
                            self.tt.testFilenames, self.tt.testXimage, self.tt.testY,
                            [], [], [],
                            self.tt.trainXfeat, self.tt.testXfeat, []]
            elif class_main.params.test_set == 'no':
                self.tt.trainXfeat = scaler.transform(self.tt.trainXfeat)
                Data = [self.tt.trainFilenames, self.tt.trainXimage, self.tt.trainY,
                        [], [], [],
                        [], [], [],
                        self.tt.trainXfeat, [], []]
        else:
            print("Set the right data type")

        if class_main.params.save_data == 'yes':
            with open(class_main.params.outpath + '/Data.pickle', 'wb') as a:
                pickle.dump(Data, a)

        if class_main.params.balance_weight == 'yes':
            with open(class_main.params.outpath + '/class_weights.pickle', 'wb') as cw:
                pickle.dump(self.tt.class_weights, cw)

        # To Save classes and filenames
        np.save(class_main.params.outpath + '/classes.npy', self.tt.lb.classes_)

        Filenames_for_Ensemble = [self.tt.trainFilenames, self.tt.testFilenames]
        with open(class_main.params.outpath + '/Filenames_for_Ensemble_training.pickle', 'wb') as b:
            pickle.dump(Filenames_for_Ensemble, b)

        return
