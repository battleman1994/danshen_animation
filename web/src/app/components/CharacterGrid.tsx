'use client';

import { motion } from 'framer-motion';
import type { SceneMode } from './types';
import { CHARACTERS } from './constants';

interface Props {
  character: string;
  characterCount: number;
  sceneMode: SceneMode;
  onCharacterChange: (id: string) => void;
  onCountChange: (n: number) => void;
}

export default function CharacterGrid({ character, characterCount, sceneMode, onCharacterChange, onCountChange }: Props) {
  return (
    <div
      className="rounded-2xl p-6"
      style={{
        background: '#ffffff',
        border: '1px solid #f0e6d8',
        boxShadow: '0 1px 3px rgba(45,45,45,0.04), 0 1px 2px rgba(45,45,45,0.02)',
      }}
    >
      <div className="flex items-center justify-between mb-5">
        <h3 className="text-base font-semibold" style={{ color: '#2d2d2d' }}>
          🎭 选择角色
        </h3>
        {sceneMode === 'dialogue' && (
          <div className="flex items-center gap-2">
            <span className="text-sm" style={{ color: '#8a8a86' }}>角色数</span>
            {[1, 2, 3].map((n) => (
              <motion.button
                key={n}
                onClick={() => onCountChange(n)}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                className="w-8 h-8 rounded-pill text-sm font-bold transition-all duration-200"
                style={{
                  background:
                    characterCount === n
                      ? 'linear-gradient(135deg, #ff6b6b, #ffa07a)'
                      : '#fef9f0',
                  color: characterCount === n ? '#ffffff' : '#8a8a86',
                  border: characterCount === n ? 'none' : '1px solid #f0e6d8',
                }}
              >
                {n}
              </motion.button>
            ))}
          </div>
        )}
      </div>

      <div className="grid grid-cols-4 sm:grid-cols-5 gap-3">
        {CHARACTERS.map((char) => {
          const isSelected = character === char.id;
          return (
            <motion.button
              key={char.id}
              onClick={() => onCharacterChange(char.id)}
              whileHover={{ y: -3, scale: 1.04 }}
              whileTap={{ scale: 0.95 }}
              className="relative p-3 rounded-2xl text-center transition-all duration-200"
              style={{
                background: isSelected
                  ? 'linear-gradient(135deg, rgba(255, 107, 107, 0.06), rgba(167, 139, 250, 0.08))'
                  : '#fef9f0',
                border: isSelected
                  ? '2px solid #a78bfa'
                  : '1px solid #f0e6d8',
                boxShadow: isSelected
                  ? '0 0 0 4px rgba(167, 139, 250, 0.1)'
                  : 'none',
              }}
            >
              <motion.div
                className="text-3xl mb-1"
                animate={isSelected ? { y: [0, -3, 0] } : {}}
                transition={{ duration: 0.6, repeat: Infinity, repeatDelay: 1.5 }}
              >
                {char.emoji}
              </motion.div>
              <div
                className="text-xs font-semibold"
                style={{ color: isSelected ? '#2d2d2d' : '#5f5f5d' }}
              >
                {char.name}
              </div>
              <div className="text-[10px] mt-0.5" style={{ color: '#8a8a86' }}>
                {char.style}
              </div>

              {isSelected && (
                <motion.div
                  layoutId="charIndicator"
                  className="absolute -top-1.5 -right-1.5 w-5 h-5 rounded-full flex items-center justify-center text-white text-[10px]"
                  style={{ background: 'linear-gradient(135deg, #ff6b6b, #a78bfa)' }}
                >
                  ✓
                </motion.div>
              )}
            </motion.button>
          );
        })}
      </div>
    </div>
  );
}
