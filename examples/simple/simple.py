#!/usr/bin/env python
from collections import namedtuple
from typing import Tuple, Any

import numpy as np
import tensorflow as tf

import tensorflow_datasets as tfds

HyperParams = namedtuple(
    "HyperParams", ["batch_size", "epochs", "hidden_layers"])


def normalize_img(image, label):
    """Normalizes images: uint8 -> float32."""

    return tf.cast(image, tf.float32) / 255., label


def prepare_data(hp: HyperParams) -> Tuple[Any, Any, Any]:
    # Load the MNIST dataset and split it into train, development and test set
    (train, dev, test), info = tfds.load(
        'mnist',
        split=['train[:90%]', 'train[90%:]', 'test'],
        shuffle_files=True,
        as_supervised=True,
        with_info=True,
    )

    train = train.map(
        normalize_img, num_parallel_calls=tf.data.AUTOTUNE)
    train = train.cache()
    train = train.shuffle(info.splits['train'].num_examples)
    train = train.batch(hp.batch_size)
    train = train.prefetch(tf.data.AUTOTUNE)

    dev = dev.map(
        normalize_img, num_parallel_calls=tf.data.AUTOTUNE)
    dev = dev.batch(hp.batch_size)
    dev = dev.cache()
    dev = dev.prefetch(tf.data.AUTOTUNE)

    test = test.map(
        normalize_img, num_parallel_calls=tf.data.AUTOTUNE)
    test = test.batch(hp.batch_size)
    test = test.cache()
    test = test.prefetch(tf.data.AUTOTUNE)

    return train, dev, test, info


def main(hp: HyperParams) -> None:
    train, dev, test, info = prepare_data(hp)

    # Create a model
    inputs = tf.keras.layers.Input(info.features["image"].shape)
    hidden = tf.keras.layers.Flatten()(inputs)
    for hidden_size in hp.hidden_layers:
        hidden = tf.keras.layers.Dense(
            hidden_size, activation=tf.nn.relu, kernel_regularizer='l2')(hidden)
    hidden = tf.keras.layers.Dropout(0.5)(hidden)
    outputs = tf.keras.layers.Dense(10, activation=tf.nn.softmax)(hidden)
    model = tf.keras.Model(inputs=inputs, outputs=outputs)

    model.compile(
        optimizer=tf.keras.optimizers.Adam(),
        loss=tf.keras.losses.SparseCategoricalCrossentropy(),
        metrics=[tf.keras.metrics.SparseCategoricalAccuracy('accuracy')]
    )

    # Early stopping set after 5 epochs
    stop_early = tf.keras.callbacks.EarlyStopping(
        monitor='val_loss', patience=5)

    model.fit(
        train,
        epochs=hp.epochs,
        validation_data=dev,
        callbacks=[stop_early]
    )

    # Evaluate the model
    test_loss, test_acc = model.evaluate(test)
    print("test loss, test acc:", test_loss, test_acc)


if __name__ == '__main__':
    hp = HyperParams(100, 20, [100, 100])
    main(hp)
