import sys
import argparse

import numpy as np
import theano

sys.setrecursionlimit(100000000)
theano.config.floatX = 'float32'

if theano.config.device.startswith('cuda'):
    import locale

    locale.setlocale(locale.LC_CTYPE, 'C.UTF-8')


def parse_args():
    parser = argparse.ArgumentParser(description='SRL SYSTEM')

    parser.add_argument('--mode', default='train', help='train/valid/test/h_arg/h_span')
    parser.add_argument('--method', default='span', help='span/base')
    parser.add_argument('--seed', type=int, default=0, help='seed')

    ##################
    # Input Datasets #
    ##################
    parser.add_argument('--train_data', help='path to train data')
    parser.add_argument('--dev_data', help='path to dev data')
    parser.add_argument('--test_data', help='path to test data')
    parser.add_argument('--data_type', default='conll05', help='conll05/conll12')
    parser.add_argument('--data_size', type=int, default=1000000, help='data size to be used')

    ##################
    # Output Options #
    ##################
    parser.add_argument('--save', action='store_true', default=False, help='parameters to be saved or not')
    parser.add_argument('--save_every_epoch', action='store_true', default=False, help='save at every epoch')
    parser.add_argument('--output_dir', type=str, default='output', help='output directory name')
    parser.add_argument('--output_fn', type=str, default=None, help='output file name')

    ##########
    # Search #
    ##########
    parser.add_argument('--search', type=str, default='argmax', help='argmax/greedy')
    parser.add_argument('--gamma', type=float, default=1.0, help='Scaling factor')

    ###################
    # NN Architecture #
    ###################
    parser.add_argument('--emb_dim', type=int, default=50, help='dimension of embeddings')
    parser.add_argument('--hidden_dim', type=int, default=32, help='dimension of hidden layer')
    parser.add_argument('--n_layers', type=int, default=1, help='number of layers')
    parser.add_argument('--rnn_unit', default='lstm', help='gru/lstm')
    parser.add_argument('--seq_label_alg', default='crf', help='softmax/crf')
    parser.add_argument('--n_experts', type=int, default=0, help='number of ensemble models')

    ####################
    # Training Options #
    ####################
    parser.add_argument('--epoch', type=int, default=100, help='number of epochs to train')
    parser.add_argument('--batch_size', type=int, default=32, help='mini-batch size')
    parser.add_argument('--word_emb', default=None, help='Initial embeddings to be loaded')
    parser.add_argument('--train_elmo_emb', default=None, help='ELMo embeddings to be loaded')
    parser.add_argument('--dev_elmo_emb', default=None, help='ELMo embeddings to be loaded')
    parser.add_argument('--test_elmo_emb', default=None, help='ELMo embeddings to be loaded')

    ########################
    # Optimization Options #
    ########################
    parser.add_argument('--lr', type=float, default=0.001, help='learning rate')
    parser.add_argument('--halve_lr', action='store_true', default=False, help='halve learning rate')
    parser.add_argument('--opt_type', default='adam', help='sgd/adam')
    parser.add_argument('--grad_clip', action='store_true', default=False, help='gradient clipping')
    parser.add_argument('--reg', type=float, default=0.0001, help='L2 Reg rate')
    parser.add_argument('--drop_rate', type=float, default=0.0, help='Dropout Rate')

    ###################
    # Loading Options #
    ###################
    parser.add_argument('--load_param', default=None, help='path to params')
    parser.add_argument('--load_param_dir', default=None, help='path to param dir')
    parser.add_argument('--load_opt_param', default=None, help='path to params')
    parser.add_argument('--load_param_latest', action='store_true', default=False, help='load the latest params')
    parser.add_argument('--load_label', default=None, help='path to labels')

    return parser.parse_args()


def main():
    argv = parse_args()
    np.random.seed(argv.seed)

    if argv.data_type == "conll05":
        from utils.loaders import Conll05Loader
        loader = Conll05Loader(argv)
    else:
        from utils.loaders import CoNLL12Loader
        loader = CoNLL12Loader(argv)

    if argv.method == "span":
        from srl.preprocessors import SpanPreprocessor
        from utils.evaluators import SpanEvaluator
        from srl.model_api import SpanModelAPI

        if argv.mode == "train":
            from srl.trainers import SpanTrainer

            SpanTrainer(argv=argv,
                        loader=loader,
                        preprocessor=SpanPreprocessor(argv),
                        evaluator=SpanEvaluator(argv),
                        model_api=SpanModelAPI(argv)
                        ).train()

        elif argv.mode == "valid":
            from srl.trainers import SpanTrainer

            SpanTrainer(argv=argv,
                        loader=loader,
                        preprocessor=SpanPreprocessor(argv),
                        evaluator=SpanEvaluator(argv),
                        model_api=SpanModelAPI(argv)
                        ).validate()

        else:
            from srl.testers import Tester
            from utils.savers import SpanSaver

            Tester(argv=argv,
                   loader=loader,
                   saver=SpanSaver(argv),
                   preprocessor=SpanPreprocessor(argv),
                   model_api=SpanModelAPI(argv)
                   ).predict()

    else:
        from srl.preprocessors import BasePreprocessor
        from utils.evaluators import Evaluator
        from srl.model_api import ModelAPI

        if argv.mode == "train":
            from srl.trainers import Trainer

            trainer = Trainer(argv=argv,
                              loader=loader,
                              preprocessor=BasePreprocessor(argv),
                              evaluator=Evaluator(argv),
                              model_api=ModelAPI(argv)
                              )
            trainer.train()

        elif argv.mode == "valid":
            from srl.trainers import Trainer

            Trainer(argv=argv,
                    loader=loader,
                    preprocessor=BasePreprocessor(argv),
                    evaluator=Evaluator(argv),
                    model_api=ModelAPI(argv)
                    ).validate()

        else:
            from srl.testers import Tester
            from utils.savers import BaseSaver

            Tester(argv=argv,
                   loader=loader,
                   saver=BaseSaver(argv),
                   preprocessor=BasePreprocessor(argv),
                   model_api=ModelAPI(argv)
                   ).predict()


if __name__ == '__main__':
    main()
