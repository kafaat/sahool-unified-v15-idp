import 'dart:typed_data';

import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/ml/tflite_helper.dart';

void main() {
  // ===========================================================================
  // TFLiteConfig Default Constructor Tests
  // ===========================================================================

  group('TFLiteConfig default constructor', () {
    test('requires modelAssetPath', () {
      const config = TFLiteConfig(
        modelAssetPath: 'assets/models/test.tflite',
        labelsAssetPath: 'assets/models/labels.txt',
        labelsArAssetPath: 'assets/models/labels_ar.txt',
      );
      expect(config.modelAssetPath, 'assets/models/test.tflite');
    });

    test('requires labelsAssetPath', () {
      const config = TFLiteConfig(
        modelAssetPath: 'assets/models/test.tflite',
        labelsAssetPath: 'assets/models/labels.txt',
        labelsArAssetPath: 'assets/models/labels_ar.txt',
      );
      expect(config.labelsAssetPath, 'assets/models/labels.txt');
    });

    test('requires labelsArAssetPath', () {
      const config = TFLiteConfig(
        modelAssetPath: 'assets/models/test.tflite',
        labelsAssetPath: 'assets/models/labels.txt',
        labelsArAssetPath: 'assets/models/labels_ar.txt',
      );
      expect(config.labelsArAssetPath, 'assets/models/labels_ar.txt');
    });

    test('default inputSize is 640', () {
      const config = TFLiteConfig(
        modelAssetPath: 'test.tflite',
        labelsAssetPath: 'labels.txt',
        labelsArAssetPath: 'labels_ar.txt',
      );
      expect(config.inputSize, 640);
    });

    test('default numThreads is 4', () {
      const config = TFLiteConfig(
        modelAssetPath: 'test.tflite',
        labelsAssetPath: 'labels.txt',
        labelsArAssetPath: 'labels_ar.txt',
      );
      expect(config.numThreads, 4);
    });

    test('default useGpu is false', () {
      const config = TFLiteConfig(
        modelAssetPath: 'test.tflite',
        labelsAssetPath: 'labels.txt',
        labelsArAssetPath: 'labels_ar.txt',
      );
      expect(config.useGpu, isFalse);
    });

    test('default useNnapi is false', () {
      const config = TFLiteConfig(
        modelAssetPath: 'test.tflite',
        labelsAssetPath: 'labels.txt',
        labelsArAssetPath: 'labels_ar.txt',
      );
      expect(config.useNnapi, isFalse);
    });

    test('default confidenceThreshold is 0.5', () {
      const config = TFLiteConfig(
        modelAssetPath: 'test.tflite',
        labelsAssetPath: 'labels.txt',
        labelsArAssetPath: 'labels_ar.txt',
      );
      expect(config.confidenceThreshold, 0.5);
    });

    test('default nmsIoUThreshold is 0.45', () {
      const config = TFLiteConfig(
        modelAssetPath: 'test.tflite',
        labelsAssetPath: 'labels.txt',
        labelsArAssetPath: 'labels_ar.txt',
      );
      expect(config.nmsIoUThreshold, 0.45);
    });

    test('default maxDetections is 100', () {
      const config = TFLiteConfig(
        modelAssetPath: 'test.tflite',
        labelsAssetPath: 'labels.txt',
        labelsArAssetPath: 'labels_ar.txt',
      );
      expect(config.maxDetections, 100);
    });

    test('custom inputSize is stored', () {
      const config = TFLiteConfig(
        modelAssetPath: 'test.tflite',
        labelsAssetPath: 'labels.txt',
        labelsArAssetPath: 'labels_ar.txt',
        inputSize: 320,
      );
      expect(config.inputSize, 320);
    });

    test('custom numThreads is stored', () {
      const config = TFLiteConfig(
        modelAssetPath: 'test.tflite',
        labelsAssetPath: 'labels.txt',
        labelsArAssetPath: 'labels_ar.txt',
        numThreads: 2,
      );
      expect(config.numThreads, 2);
    });

    test('custom useGpu is stored', () {
      const config = TFLiteConfig(
        modelAssetPath: 'test.tflite',
        labelsAssetPath: 'labels.txt',
        labelsArAssetPath: 'labels_ar.txt',
        useGpu: true,
      );
      expect(config.useGpu, isTrue);
    });

    test('custom useNnapi is stored', () {
      const config = TFLiteConfig(
        modelAssetPath: 'test.tflite',
        labelsAssetPath: 'labels.txt',
        labelsArAssetPath: 'labels_ar.txt',
        useNnapi: true,
      );
      expect(config.useNnapi, isTrue);
    });

    test('custom confidenceThreshold is stored', () {
      const config = TFLiteConfig(
        modelAssetPath: 'test.tflite',
        labelsAssetPath: 'labels.txt',
        labelsArAssetPath: 'labels_ar.txt',
        confidenceThreshold: 0.7,
      );
      expect(config.confidenceThreshold, 0.7);
    });

    test('custom nmsIoUThreshold is stored', () {
      const config = TFLiteConfig(
        modelAssetPath: 'test.tflite',
        labelsAssetPath: 'labels.txt',
        labelsArAssetPath: 'labels_ar.txt',
        nmsIoUThreshold: 0.6,
      );
      expect(config.nmsIoUThreshold, 0.6);
    });

    test('custom maxDetections is stored', () {
      const config = TFLiteConfig(
        modelAssetPath: 'test.tflite',
        labelsAssetPath: 'labels.txt',
        labelsArAssetPath: 'labels_ar.txt',
        maxDetections: 200,
      );
      expect(config.maxDetections, 200);
    });
  });

  // ===========================================================================
  // TFLiteConfig.pestDetection Preset Tests
  // ===========================================================================

  group('TFLiteConfig.pestDetection', () {
    test('modelAssetPath is yolo26_pests.tflite', () {
      expect(
        TFLiteConfig.pestDetection.modelAssetPath,
        'assets/models/yolo26_pests.tflite',
      );
    });

    test('labelsAssetPath is labels_pests.txt', () {
      expect(
        TFLiteConfig.pestDetection.labelsAssetPath,
        'assets/models/labels_pests.txt',
      );
    });

    test('labelsArAssetPath is labels_pests_ar.txt', () {
      expect(
        TFLiteConfig.pestDetection.labelsArAssetPath,
        'assets/models/labels_pests_ar.txt',
      );
    });

    test('inputSize is 640', () {
      expect(TFLiteConfig.pestDetection.inputSize, 640);
    });

    test('confidenceThreshold is 0.5', () {
      expect(TFLiteConfig.pestDetection.confidenceThreshold, 0.5);
    });

    test('maxDetections uses default 100', () {
      expect(TFLiteConfig.pestDetection.maxDetections, 100);
    });

    test('nmsIoUThreshold uses default 0.45', () {
      expect(TFLiteConfig.pestDetection.nmsIoUThreshold, 0.45);
    });

    test('numThreads uses default 4', () {
      expect(TFLiteConfig.pestDetection.numThreads, 4);
    });

    test('useGpu uses default false', () {
      expect(TFLiteConfig.pestDetection.useGpu, isFalse);
    });

    test('useNnapi uses default false', () {
      expect(TFLiteConfig.pestDetection.useNnapi, isFalse);
    });
  });

  // ===========================================================================
  // TFLiteConfig.diseaseDetection Preset Tests
  // ===========================================================================

  group('TFLiteConfig.diseaseDetection', () {
    test('modelAssetPath is yolo26_diseases.tflite', () {
      expect(
        TFLiteConfig.diseaseDetection.modelAssetPath,
        'assets/models/yolo26_diseases.tflite',
      );
    });

    test('labelsAssetPath is labels_diseases.txt', () {
      expect(
        TFLiteConfig.diseaseDetection.labelsAssetPath,
        'assets/models/labels_diseases.txt',
      );
    });

    test('labelsArAssetPath is labels_diseases_ar.txt', () {
      expect(
        TFLiteConfig.diseaseDetection.labelsArAssetPath,
        'assets/models/labels_diseases_ar.txt',
      );
    });

    test('inputSize is 640', () {
      expect(TFLiteConfig.diseaseDetection.inputSize, 640);
    });

    test('confidenceThreshold is 0.5', () {
      expect(TFLiteConfig.diseaseDetection.confidenceThreshold, 0.5);
    });

    test('maxDetections uses default 100', () {
      expect(TFLiteConfig.diseaseDetection.maxDetections, 100);
    });

    test('nmsIoUThreshold uses default 0.45', () {
      expect(TFLiteConfig.diseaseDetection.nmsIoUThreshold, 0.45);
    });

    test('numThreads uses default 4', () {
      expect(TFLiteConfig.diseaseDetection.numThreads, 4);
    });

    test('useGpu uses default false', () {
      expect(TFLiteConfig.diseaseDetection.useGpu, isFalse);
    });

    test('useNnapi uses default false', () {
      expect(TFLiteConfig.diseaseDetection.useNnapi, isFalse);
    });
  });

  // ===========================================================================
  // TFLiteConfig.plantCounting Preset Tests
  // ===========================================================================

  group('TFLiteConfig.plantCounting', () {
    test('modelAssetPath is yolo26_plants.tflite', () {
      expect(
        TFLiteConfig.plantCounting.modelAssetPath,
        'assets/models/yolo26_plants.tflite',
      );
    });

    test('labelsAssetPath is labels_plants.txt', () {
      expect(
        TFLiteConfig.plantCounting.labelsAssetPath,
        'assets/models/labels_plants.txt',
      );
    });

    test('labelsArAssetPath is labels_plants_ar.txt', () {
      expect(
        TFLiteConfig.plantCounting.labelsArAssetPath,
        'assets/models/labels_plants_ar.txt',
      );
    });

    test('inputSize is 640', () {
      expect(TFLiteConfig.plantCounting.inputSize, 640);
    });

    test('confidenceThreshold is 0.4 (lower for counting)', () {
      expect(TFLiteConfig.plantCounting.confidenceThreshold, 0.4);
    });

    test('maxDetections is 500 (higher for counting)', () {
      expect(TFLiteConfig.plantCounting.maxDetections, 500);
    });

    test('nmsIoUThreshold uses default 0.45', () {
      expect(TFLiteConfig.plantCounting.nmsIoUThreshold, 0.45);
    });

    test('numThreads uses default 4', () {
      expect(TFLiteConfig.plantCounting.numThreads, 4);
    });

    test('useGpu uses default false', () {
      expect(TFLiteConfig.plantCounting.useGpu, isFalse);
    });

    test('useNnapi uses default false', () {
      expect(TFLiteConfig.plantCounting.useNnapi, isFalse);
    });
  });

  // ===========================================================================
  // Cross-Preset Comparison Tests
  // ===========================================================================

  group('TFLiteConfig preset comparisons', () {
    test('all presets use 640 input size', () {
      expect(TFLiteConfig.pestDetection.inputSize, 640);
      expect(TFLiteConfig.diseaseDetection.inputSize, 640);
      expect(TFLiteConfig.plantCounting.inputSize, 640);
    });

    test('plantCounting has lower confidence threshold than pest/disease', () {
      expect(
        TFLiteConfig.plantCounting.confidenceThreshold,
        lessThan(TFLiteConfig.pestDetection.confidenceThreshold),
      );
      expect(
        TFLiteConfig.plantCounting.confidenceThreshold,
        lessThan(TFLiteConfig.diseaseDetection.confidenceThreshold),
      );
    });

    test('plantCounting has higher maxDetections than pest/disease', () {
      expect(
        TFLiteConfig.plantCounting.maxDetections,
        greaterThan(TFLiteConfig.pestDetection.maxDetections),
      );
      expect(
        TFLiteConfig.plantCounting.maxDetections,
        greaterThan(TFLiteConfig.diseaseDetection.maxDetections),
      );
    });

    test('pest and disease presets share same confidence threshold', () {
      expect(
        TFLiteConfig.pestDetection.confidenceThreshold,
        TFLiteConfig.diseaseDetection.confidenceThreshold,
      );
    });

    test('pest and disease presets share same maxDetections', () {
      expect(
        TFLiteConfig.pestDetection.maxDetections,
        TFLiteConfig.diseaseDetection.maxDetections,
      );
    });

    test('all presets have distinct model paths', () {
      final paths = {
        TFLiteConfig.pestDetection.modelAssetPath,
        TFLiteConfig.diseaseDetection.modelAssetPath,
        TFLiteConfig.plantCounting.modelAssetPath,
      };
      expect(paths.length, 3);
    });

    test('all presets have distinct label paths', () {
      final paths = {
        TFLiteConfig.pestDetection.labelsAssetPath,
        TFLiteConfig.diseaseDetection.labelsAssetPath,
        TFLiteConfig.plantCounting.labelsAssetPath,
      };
      expect(paths.length, 3);
    });

    test('all presets have distinct Arabic label paths', () {
      final paths = {
        TFLiteConfig.pestDetection.labelsArAssetPath,
        TFLiteConfig.diseaseDetection.labelsArAssetPath,
        TFLiteConfig.plantCounting.labelsArAssetPath,
      };
      expect(paths.length, 3);
    });

    test('all presets use same default nmsIoUThreshold', () {
      expect(TFLiteConfig.pestDetection.nmsIoUThreshold, 0.45);
      expect(TFLiteConfig.diseaseDetection.nmsIoUThreshold, 0.45);
      expect(TFLiteConfig.plantCounting.nmsIoUThreshold, 0.45);
    });

    test('all preset model paths end with .tflite', () {
      expect(TFLiteConfig.pestDetection.modelAssetPath, endsWith('.tflite'));
      expect(
          TFLiteConfig.diseaseDetection.modelAssetPath, endsWith('.tflite'));
      expect(TFLiteConfig.plantCounting.modelAssetPath, endsWith('.tflite'));
    });

    test('all preset label paths end with .txt', () {
      expect(TFLiteConfig.pestDetection.labelsAssetPath, endsWith('.txt'));
      expect(
          TFLiteConfig.diseaseDetection.labelsAssetPath, endsWith('.txt'));
      expect(TFLiteConfig.plantCounting.labelsAssetPath, endsWith('.txt'));
    });

    test('all preset model paths start with assets/models/', () {
      expect(TFLiteConfig.pestDetection.modelAssetPath,
          startsWith('assets/models/'));
      expect(TFLiteConfig.diseaseDetection.modelAssetPath,
          startsWith('assets/models/'));
      expect(TFLiteConfig.plantCounting.modelAssetPath,
          startsWith('assets/models/'));
    });
  });

  // ===========================================================================
  // TFLiteException Tests
  // ===========================================================================

  group('TFLiteException', () {
    test('stores message', () {
      final ex = TFLiteException('error msg', 'رسالة الخطأ');
      expect(ex.message, 'error msg');
    });

    test('stores messageAr', () {
      final ex = TFLiteException('error msg', 'رسالة الخطأ');
      expect(ex.messageAr, 'رسالة الخطأ');
    });

    test('cause defaults to null', () {
      final ex = TFLiteException('error', 'خطأ');
      expect(ex.cause, isNull);
    });

    test('cause is stored when provided', () {
      final cause = Exception('underlying');
      final ex = TFLiteException('error', 'خطأ', cause: cause);
      expect(ex.cause, cause);
    });

    test('toString includes message', () {
      final ex = TFLiteException('Failed to load', 'فشل التحميل');
      expect(ex.toString(), contains('Failed to load'));
    });

    test('toString includes cause when present', () {
      final cause = Exception('bad file');
      final ex = TFLiteException('Failed', 'فشل', cause: cause);
      expect(ex.toString(), contains('bad file'));
    });

    test('toString does not include cause parenthetical when null', () {
      final ex = TFLiteException('Failed', 'فشل');
      expect(ex.toString(), 'TFLiteException: Failed');
    });

    test('implements Exception interface', () {
      final ex = TFLiteException('test', 'اختبار');
      expect(ex, isA<Exception>());
    });
  });

  // ===========================================================================
  // PreprocessedImage Tests
  // ===========================================================================

  group('PreprocessedImage', () {
    test('stores inputTensor', () {
      final tensor = Float32List.fromList([0.0, 0.5, 1.0]);
      final img = PreprocessedImage(
        inputTensor: tensor,
        originalWidth: 1920,
        originalHeight: 1080,
        scaleX: 0.333,
        scaleY: 0.333,
        padLeft: 0,
        padTop: 93,
      );
      expect(img.inputTensor, tensor);
    });

    test('stores original dimensions', () {
      final img = PreprocessedImage(
        inputTensor: Float32List(3),
        originalWidth: 4032,
        originalHeight: 3024,
        scaleX: 0.159,
        scaleY: 0.159,
        padLeft: 0,
        padTop: 80,
      );
      expect(img.originalWidth, 4032);
      expect(img.originalHeight, 3024);
    });

    test('stores scale factors', () {
      final img = PreprocessedImage(
        inputTensor: Float32List(3),
        originalWidth: 1920,
        originalHeight: 1080,
        scaleX: 0.5,
        scaleY: 0.5,
        padLeft: 10,
        padTop: 20,
      );
      expect(img.scaleX, 0.5);
      expect(img.scaleY, 0.5);
    });

    test('stores padding values', () {
      final img = PreprocessedImage(
        inputTensor: Float32List(3),
        originalWidth: 640,
        originalHeight: 480,
        scaleX: 1.0,
        scaleY: 1.0,
        padLeft: 0,
        padTop: 80,
      );
      expect(img.padLeft, 0);
      expect(img.padTop, 80);
    });
  });
}
