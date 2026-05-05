'use client';

import { motion } from 'framer-motion';
import { fadeUp } from './animations';

export default function Footer() {
  return (
    <motion.div
      initial="hidden"
      animate="visible"
      variants={fadeUp}
      transition={{ delay: 0.3 }}
      className="mt-14 text-center text-sm"
      style={{ color: '#b0aca4' }}
    >
      <p className="font-medium">🔥 蛋生动画 — AI 动漫视频生成器</p>
      <p className="mt-1">支持 iOS · Web · Windows | MIT License</p>
    </motion.div>
  );
}
