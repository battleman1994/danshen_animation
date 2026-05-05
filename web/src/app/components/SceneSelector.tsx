'use client';

import { motion } from 'framer-motion';
import { fadeUp } from './animations';
import type { SceneMode } from './types';
import { SCENES } from './constants';

interface Props {
  sceneMode: SceneMode;
  onChange: (mode: SceneMode) => void;
}

export default function SceneSelector({ sceneMode, onChange }: Props) {
  return (
    <motion.div
      initial="hidden"
      animate="visible"
      variants={fadeUp}
      className="mb-8"
    >
      <h3 className="text-xs font-semibold uppercase tracking-[0.1em] mb-3" style={{ color: '#8a8a86' }}>
        选择场景
      </h3>
      <div className="grid grid-cols-3 gap-3">
        {SCENES.map((scene) => {
          const Icon = scene.icon;
          const isSelected = sceneMode === scene.id;
          return (
            <motion.button
              key={scene.id}
              onClick={() => onChange(scene.id)}
              whileHover={{ y: -2 }}
              whileTap={{ scale: 0.97 }}
              className="relative p-4 rounded-2xl text-center transition-all duration-200"
              style={{
                background: isSelected
                  ? 'linear-gradient(135deg, rgba(255, 107, 107, 0.08), rgba(167, 139, 250, 0.1))'
                  : '#ffffff',
                border: isSelected
                  ? '1.5px solid rgba(167, 139, 250, 0.4)'
                  : '1px solid #f0e6d8',
                boxShadow: isSelected
                  ? '0 2px 12px rgba(167, 139, 250, 0.1)'
                  : '0 1px 3px rgba(45,45,45,0.03)',
              }}
            >
              <Icon
                size={22}
                className="mx-auto mb-1.5"
                style={{ color: isSelected ? '#a78bfa' : '#8a8a86' }}
              />
              <div
                className="font-semibold text-sm"
                style={{ color: isSelected ? '#2d2d2d' : '#5f5f5d' }}
              >
                {scene.name}
              </div>
              <div className="text-xs mt-0.5" style={{ color: '#8a8a86' }}>
                {scene.desc}
              </div>
            </motion.button>
          );
        })}
      </div>
    </motion.div>
  );
}
