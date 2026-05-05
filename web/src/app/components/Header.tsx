'use client';

import { motion } from 'framer-motion';
import { Sparkles } from 'lucide-react';
import { fadeUp } from './animations';

export default function Header() {
  return (
    <motion.div
      initial="hidden"
      animate="visible"
      variants={fadeUp}
      className="text-center mb-12"
    >
      <motion.div
        className="inline-flex items-center gap-2 px-4 py-1.5 rounded-pill mb-5 text-sm font-medium"
        style={{
          background: 'linear-gradient(135deg, rgba(255, 107, 107, 0.1), rgba(167, 139, 250, 0.1))',
          color: '#a78bfa',
          border: '1px solid rgba(167, 139, 250, 0.15)',
        }}
        whileHover={{ scale: 1.02 }}
      >
        <Sparkles size={14} />
        AI 动漫视频生成器
      </motion.div>

      <h1
        className="text-5xl md:text-6xl font-bold mb-4 tracking-[-0.02em]"
        style={{
          background: 'linear-gradient(135deg, #ff6b6b 0%, #ffa07a 50%, #a78bfa 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text',
        }}
      >
        🔥 蛋生动画
      </h1>
      <p
        className="text-lg"
        style={{
          color: '#5f5f5d',
          maxWidth: '420px',
          margin: '0 auto',
          lineHeight: 1.6,
        }}
      >
        输入热点话题，AI 为你生成可爱动物主演的动漫视频
      </p>
    </motion.div>
  );
}
