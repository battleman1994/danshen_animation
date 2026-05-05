'use client';

import { motion } from 'framer-motion';
import { fadeUp } from './animations';
import { STYLES } from './constants';

interface Props {
  style: string;
  onChange: (id: string) => void;
}

export default function StyleSelector({ style, onChange }: Props) {
  return (
    <motion.div
      initial="hidden"
      animate="visible"
      variants={fadeUp}
      transition={{ delay: 0.2 }}
      className="mb-8 rounded-2xl p-5"
      style={{
        background: '#ffffff',
        border: '1px solid #f0e6d8',
        boxShadow: '0 1px 3px rgba(45,45,45,0.04), 0 1px 2px rgba(45,45,45,0.02)',
      }}
    >
      <h3 className="text-sm font-semibold mb-3" style={{ color: '#5f5f5d' }}>
        风格
      </h3>
      <div className="flex gap-2 flex-wrap">
        {STYLES.map((s) => {
          const isActive = style === s.id;
          return (
            <motion.button
              key={s.id}
              onClick={() => onChange(s.id)}
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
              className="px-5 py-2 rounded-pill text-sm font-medium transition-all duration-200"
              style={{
                background: isActive
                  ? 'linear-gradient(135deg, #ff6b6b, #ffa07a)'
                  : '#fef9f0',
                color: isActive ? '#ffffff' : '#5f5f5d',
                border: isActive ? 'none' : '1px solid #f0e6d8',
                boxShadow: isActive ? '0 2px 8px rgba(255, 107, 107, 0.2)' : 'none',
              }}
            >
              {s.label}
            </motion.button>
          );
        })}
      </div>
    </motion.div>
  );
}
