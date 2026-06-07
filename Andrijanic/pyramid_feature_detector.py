#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Feature Detection on Image Pyramid
Erkennt Features auf 8-stufiger Bildpyramide (1.2^k Skalierung)
und berechnet ihre Positionen im Original-Bild.
"""

import cv2
import numpy as np
from pathlib import Path
import json
from collections import defaultdict
import sys
import io

# UTF-8 Encoding für Console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class PyramidFeatureDetector:
    def __init__(self, cam0_path, output_path):
        self.cam0_path = Path(cam0_path)
        self.output_path = Path(output_path)
        self.scale_factor = 1.2
        self.num_stages = 8  # k=0-7
        self.results = {}

    def get_image_files(self):
        """Hole alle PNG-Dateien aus cam0 Ordner, sortiert"""
        images = sorted(self.cam0_path.glob("*.png"))
        return images

    def create_pyramid(self, image):
        """Erstelle 8-stufige Pyramide mit 1.2^k Skalierung"""
        pyramid = []
        original_h, original_w = image.shape[:2]

        for k in range(self.num_stages):
            scale = self.scale_factor ** k
            new_w = int(original_w / scale)
            new_h = int(original_h / scale)

            resized = cv2.resize(image, (new_w, new_h))
            pyramid.append({
                'k': k,
                'image': resized,
                'size': (new_w, new_h),
                'scale': scale
            })

        return pyramid

    def detect_features_on_pyramid(self, pyramid, image_name):
        """Erkenne Features auf jeder Stufe der Pyramide"""

        # FAST Feature Detector
        fast = cv2.FastFeatureDetector_create(threshold=20)

        # Speichere Features pro Stufe
        all_features = defaultdict(list)  # k -> [(x, y, strength)]

        for stage in pyramid:
            k = stage['k']
            gray = cv2.cvtColor(stage['image'], cv2.COLOR_BGR2GRAY) if len(stage['image'].shape) == 3 else stage['image']

            # Erkenne Keypoints
            keypoints = fast.detect(gray, None)

            for kp in keypoints:
                x_k = kp.pt[0]
                y_k = kp.pt[1]
                strength = kp.response

                all_features[k].append({
                    'x_k': x_k,
                    'y_k': y_k,
                    'strength': strength
                })

        return all_features

    def backproject_to_original(self, all_features):
        """Berechne Positionen im Original-Bild"""
        backprojected = {}

        for k, features_on_stage in all_features.items():
            scale = self.scale_factor ** k
            backprojected[k] = []

            for feature in features_on_stage:
                x_k = feature['x_k']
                y_k = feature['y_k']

                # Hochrechnung: x_original = x_k * 1.2^k
                x_orig = int(x_k * scale)
                y_orig = int(y_k * scale)

                backprojected[k].append({
                    'x_k': x_k,
                    'y_k': y_k,
                    'x_original': x_orig,
                    'y_original': y_orig,
                    'strength': feature['strength'],
                    'stage': k
                })

        return backprojected

    def remove_duplicates(self, backprojected, threshold=10):
        """Entferne Duplikate - gleiche Features aus unterschiedlichen Stufen"""

        # Sammle ALLE unique Features basierend auf Original-Position
        unique_features = {}

        for k in sorted(backprojected.keys()):
            for feature in backprojected[k]:
                x_orig = feature['x_original']
                y_orig = feature['y_original']

                # Suche ob diese Position schon existiert
                found_duplicate = False
                for existing_id, existing_feature in unique_features.items():
                    ex_x = existing_feature['x_original']
                    ex_y = existing_feature['y_original']

                    # Berechne Distanz
                    dist = np.sqrt((x_orig - ex_x)**2 + (y_orig - ex_y)**2)

                    if dist < threshold:
                        # Duplikat gefunden - füge Stufe hinzu
                        if feature['stage'] not in existing_feature['detected_on_stages']:
                            existing_feature['detected_on_stages'].append(feature['stage'])

                        # Update auf stärkere Feature wenn nötig
                        if feature['strength'] > existing_feature['strongest_strength']:
                            existing_feature['strongest_strength'] = feature['strength']
                            existing_feature['strongest_on_stage'] = feature['stage']

                        found_duplicate = True
                        break

                if not found_duplicate:
                    # Neue Feature
                    feature_id = len(unique_features)
                    unique_features[feature_id] = {
                        'x_original': x_orig,
                        'y_original': y_orig,
                        'detected_on_stages': [k],
                        'strongest_on_stage': k,
                        'strongest_strength': feature['strength']
                    }

        return unique_features

    def filter_small_stages_only(self, unique_features):
        """Behalte nur Features die auf k>=5 erkannt werden"""

        filtered = {}
        for feature_id, feature in unique_features.items():
            stages = feature['detected_on_stages']

            # Prüfe: nur auf kleinen Stufen (k=5,6,7) erkannt?
            only_small_stages = all(s >= 5 for s in stages)

            # Oder: auf k=6,7 erkannt aber NICHT auf k=0-5?
            has_large_stages = any(s < 5 for s in stages)
            has_small_stages = any(s >= 5 for s in stages)

            feature['only_on_small_stages'] = has_small_stages and not has_large_stages

            # Speichere alle Features für Statistik
            filtered[feature_id] = feature

        return filtered

    def process_image(self, image_path):
        """Verarbeite ein einzelnes Bild"""

        print(f"\n{'='*70}")
        print(f"Verarbeite: {image_path.name}")
        print(f"{'='*70}")

        # Lade Bild
        image = cv2.imread(str(image_path))
        if image is None:
            print(f"❌ Konnte Bild nicht laden: {image_path}")
            return None

        original_h, original_w = image.shape[:2]
        print(f"✓ Original-Größe: {original_w}×{original_h}")

        # Erstelle Pyramide
        pyramid = self.create_pyramid(image)
        print(f"✓ Pyramide erstellt:")
        for stage in pyramid:
            w, h = stage['size']
            print(f"  Stufe {stage['k']}: {w}×{h} (scale={stage['scale']:.2f})")

        # Erkenne Features
        all_features = self.detect_features_on_pyramid(pyramid, image_path.name)

        # Zähle Features pro Stufe
        for k in sorted(all_features.keys()):
            count = len(all_features[k])
            print(f"✓ Stufe {k}: {count} Features erkannt")

        # Hochrechnung
        backprojected = self.backproject_to_original(all_features)

        # Duplikate entfernen
        unique_features = self.remove_duplicates(backprojected, threshold=10)
        print(f"✓ Nach Duplikat-Entfernung: {len(unique_features)} unique Features")

        # Filter: nur kleine Stufen
        filtered_features = self.filter_small_stages_only(unique_features)

        # Statistik
        small_only = sum(1 for f in filtered_features.values() if f['only_on_small_stages'])
        large_and_small = sum(1 for f in filtered_features.values() if not f['only_on_small_stages'])

        print(f"✓ Features nur auf k>=5: {small_only}")
        print(f"✓ Features auf allen Stufen: {large_and_small}")

        # Speichere Results
        return {
            'filename': image_path.name,
            'original_size': [original_w, original_h],
            'total_features': len(filtered_features),
            'only_small_stages': small_only,
            'all_stages': large_and_small,
            'features': filtered_features
        }

    def run(self):
        """Verarbeite alle Bilder"""

        images = self.get_image_files()
        print(f"\n🔍 Gefunden {len(images)} Bilder in {self.cam0_path}")

        for idx, image_path in enumerate(images):
            result = self.process_image(image_path)

            if result:
                image_key = f"image_{idx}"
                self.results[image_key] = result

        # Speichere Results
        self.save_results()

        # Zeige Statistik
        self.print_statistics()

    def save_results(self):
        """Speichere Results als JSON"""

        output_file = self.output_path / "pyramid_features_results.json"

        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"\n✓ Ergebnisse gespeichert: {output_file}")

    def print_statistics(self):
        """Zeige Statistik"""

        print(f"\n{'='*70}")
        print("📊 STATISTIK")
        print(f"{'='*70}")

        total_images = len(self.results)
        total_features = sum(r['total_features'] for r in self.results.values())
        total_small_only = sum(r['only_small_stages'] for r in self.results.values())
        total_all_stages = sum(r['all_stages'] for r in self.results.values())

        print(f"Verarbeitete Bilder: {total_images}")
        print(f"Gesamt Features: {total_features}")
        print(f"  - Nur auf k>=5: {total_small_only}")
        print(f"  - Auf allen Stufen: {total_all_stages}")

        if total_features > 0:
            pct_small = (total_small_only / total_features) * 100
            print(f"\nProzentsatz nur auf k>=5: {pct_small:.1f}%")


if __name__ == "__main__":
    cam0_path = Path("C:/Users/nedi2/Desktop/VC26/vcde-9-2/cam0")
    output_path = Path("C:/Users/nedi2/Desktop/VC26/vcde-9-2/Andrijanic")

    detector = PyramidFeatureDetector(cam0_path, output_path)
    detector.run()
