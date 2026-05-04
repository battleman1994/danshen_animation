// 单身动画 — 主要的动画生成页面

'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Sparkles, Upload, Link, Type, Play } from 'lucide-react';

const CHARACTERS = [
  { id: 'tabby_cat', name: '狸花猫', emoji: '🐱' },
  { id: 'brown_bear', name: '棕熊', emoji: '🐻' },
  { id: 'little_fox', name: '小狐狸', emoji: '🦊' },
  { id: 'panda', name: '熊猫', emoji: '🐼' },
  { id: 'rabbit', name: '兔子', emoji: '🐰' },
  { id: 'shiba_inu', name: '柴犬', emoji: '🐶' },
  { id: 'owl', name: '猫头鹰', emoji: '🦉' },
  { id: 'penguin', name: '企鹅', emoji: '🐧' },
];

export default function Home() {
  const [source, setSource] = useState('');
  const [sourceType, setSourceType] = useState('text');
  const [character, setCharacter] = useState('tabby_cat');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<string | null>(null);

  const handleSubmit = async () => {
    if (!source.trim()) return;
    setLoading(true);
    setResult(null);

    try {
      const res = await fetch('/api/v1/animate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source, source_type: sourceType, character }),
      });
      const data = await res.json();

      // 轮询等待
      const poll = async () => {
        const statusRes = await fetch(`/api/v1/tasks/${data.task_id}`);
        const status = await statusRes.json();
        if (status.status === 'completed') {
          setResult(status.result.video_url);
          setLoading(false);
        } else if (status.status === 'failed') {
          setLoading(false);
          alert('生成失败: ' + status.error);
        } else {
          setTimeout(poll, 3000);
        }
      };
      setTimeout(poll, 3000);
    } catch (e) {
      setLoading(false);
      alert('请求失败');
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-pink-50 via-purple-50 to-blue-50">
      <div className="max-w-2xl mx-auto px-4 py-16">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-5xl font-bold mb-4">
            🔥 单身动画
          </h1>
          <p className="text-xl text-gray-600">
            AI 驱动的动漫风格视频生成器 — 输入热点，生成萌宠视频！
          </p>
        </motion.div>

        {/* Input Tabs */}
        <div className="flex gap-2 mb-6 justify-center">
          {[
            { type: 'text', icon: Type, label: '文字' },
            { type: 'web_link', icon: Link, label: '链接' },
            { type: 'image', icon: Upload, label: '图片' },
            { type: 'douyin_video', icon: Play, label: '抖音' },
          ].map(({ type, icon: Icon, label }) => (
            <button
              key={type}
              onClick={() => setSourceType(type)}
              className={`flex items-center gap-2 px-4 py-2 rounded-full transition-all ${
                sourceType === type
                  ? 'bg-purple-600 text-white shadow-lg'
                  : 'bg-white text-gray-600 hover:bg-purple-100'
              }`}
            >
              <Icon size={18} />
              {label}
            </button>
          ))}
        </div>

        {/* Source Input */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-white rounded-2xl shadow-xl p-6 mb-6"
        >
          <textarea
            value={source}
            onChange={(e) => setSource(e.target.value)}
            placeholder={
              sourceType === 'text'
                ? '输入你想改编的内容...\n例如：今天天气真好，我们去野餐吧！'
                : sourceType === 'web_link'
                ? '粘贴网页链接...'
                : sourceType === 'douyin_video'
                ? '粘贴抖音视频链接...'
                : '上传或粘贴图片...'
            }
            className="w-full h-32 p-4 border border-gray-200 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-purple-400"
          />
        </motion.div>

        {/* Character Selection */}
        <div className="bg-white rounded-2xl shadow-xl p-6 mb-6">
          <h3 className="text-lg font-semibold mb-4">选择角色</h3>
          <div className="grid grid-cols-4 gap-3">
            {CHARACTERS.map((char) => (
              <button
                key={char.id}
                onClick={() => setCharacter(char.id)}
                className={`p-3 rounded-xl text-center transition-all ${
                  character === char.id
                    ? 'bg-purple-100 ring-2 ring-purple-400 scale-105'
                    : 'bg-gray-50 hover:bg-purple-50'
                }`}
              >
                <div className="text-3xl mb-1">{char.emoji}</div>
                <div className="text-xs text-gray-600">{char.name}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Submit */}
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={handleSubmit}
          disabled={loading || !source.trim()}
          className="w-full py-4 bg-gradient-to-r from-purple-600 to-pink-500 text-white rounded-2xl font-bold text-lg shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ repeat: Infinity, duration: 1 }}
              >
                <Sparkles size={24} />
              </motion.div>
              生成中...
            </>
          ) : (
            <>
              <Sparkles size={24} />
              生成动漫视频
            </>
          )}
        </motion.button>

        {/* Result */}
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-8 bg-white rounded-2xl shadow-xl p-6"
          >
            <h3 className="text-lg font-semibold mb-4">✨ 生成完成！</h3>
            <video
              src={result}
              controls
              className="w-full rounded-xl"
              poster="/placeholder-thumb.jpg"
            />
            <a
              href={result}
              download
              className="mt-4 block text-center py-3 bg-green-500 text-white rounded-xl font-semibold hover:bg-green-600 transition-colors"
            >
              下载视频
            </a>
          </motion.div>
        )}
      </div>
    </main>
  );
}
