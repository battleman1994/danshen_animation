// 单身动画 — 主要动画生成页面（增强版）
// 支持场景切换：对话剧场 / 新闻播报 / 自由模式

'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, Upload, Link, Type, Play, Newspaper, MessageCircle, Zap, Download, RotateCcw } from 'lucide-react';

const CHARACTERS = [
  { id: 'tabby_cat', name: '狸花猫', emoji: '🐱', style: '活泼灵巧' },
  { id: 'brown_bear', name: '棕熊', emoji: '🐻', style: '稳重憨厚' },
  { id: 'little_fox', name: '小狐狸', emoji: '🦊', style: '机灵俏皮' },
  { id: 'panda', name: '熊猫', emoji: '🐼', style: '呆萌可爱' },
  { id: 'rabbit', name: '兔子', emoji: '🐰', style: '温柔敏捷' },
  { id: 'shiba_inu', name: '柴犬', emoji: '🐶', style: '忠诚阳光' },
  { id: 'owl', name: '猫头鹰', emoji: '🦉', style: '智慧专业' },
  { id: 'penguin', name: '企鹅', emoji: '🐧', style: '憨态可掬' },
  { id: 'lion', name: '雄狮', emoji: '🦁', style: '庄重威严' },
];

const SCENES = [
  { id: 'auto', name: '智能识别', icon: Zap, desc: 'AI 自动选择最佳模式' },
  { id: 'dialogue', name: '对话剧场', icon: MessageCircle, desc: '抖音对话 → 动物演绎' },
  { id: 'news', name: '新闻播报', icon: Newspaper, desc: '热点新闻 → 动物主播' },
];

const INPUT_TABS = [
  { type: 'text', icon: Type, label: '文字' },
  { type: 'web_link', icon: Link, label: '链接' },
  { type: 'image', icon: Upload, label: '图片' },
  { type: 'douyin_video', icon: Play, label: '抖音' },
] as const;

type SceneMode = 'auto' | 'dialogue' | 'news';
type SourceType = 'text' | 'web_link' | 'image' | 'douyin_video';

export default function Home() {
  const [sceneMode, setSceneMode] = useState<SceneMode>('auto');
  const [source, setSource] = useState('');
  const [sourceType, setSourceType] = useState<SourceType>('text');
  const [character, setCharacter] = useState('tabby_cat');
  const [characterCount, setCharacterCount] = useState(2);
  const [style, setStyle] = useState('auto');
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [statusText, setStatusText] = useState('');
  const [result, setResult] = useState<string | null>(null);

  const handleSubmit = async () => {
    if (!source.trim()) return;
    setLoading(true);
    setProgress(0);
    setStatusText('排队中...');
    setResult(null);

    try {
      const res = await fetch('/api/v1/animate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source,
          source_type: sourceType,
          character,
          character_count: characterCount,
          style,
          scene_mode: sceneMode,
        }),
      });
      const data = await res.json();

      if (!data.task_id) {
        throw new Error('任务创建失败');
      }

      // 轮询等待
      const poll = async () => {
        try {
          const statusRes = await fetch(`/api/v1/tasks/${data.task_id}`);
          const status = await statusRes.json();

          setProgress(status.progress || 0);
          setStatusText(getStatusLabel(status.status));

          if (status.status === 'completed') {
            setProgress(100);
            setStatusText('✨ 生成完成！');
            setResult(status.result?.video_url || null);
            setLoading(false);
          } else if (status.status === 'failed') {
            setLoading(false);
            setStatusText('生成失败: ' + (status.error || '未知错误'));
            alert('生成失败: ' + status.error);
          } else {
            setTimeout(poll, 2000);
          }
        } catch {
          setTimeout(poll, 2000);
        }
      };
      setTimeout(poll, 2000);
    } catch (e: any) {
      setLoading(false);
      setStatusText('请求失败');
      alert('请求失败: ' + e.message);
    }
  };

  const getStatusLabel = (status: string): string => {
    const labels: Record<string, string> = {
      queued: '⏳ 排队中...',
      extracting: '📥 正在提取内容...',
      adapting: '✍️ 正在改编脚本...',
      generating_characters: '🎨 正在生成角色...',
      synthesizing_voice: '🔊 正在合成语音...',
      composing_video: '🎬 正在合成视频...',
      completed: '✨ 生成完成！',
    };
    return labels[status] || status;
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-pink-50 via-purple-50 to-blue-50">
      <div className="max-w-2xl mx-auto px-4 py-10">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-10"
        >
          <h1 className="text-5xl font-bold mb-3 bg-gradient-to-r from-purple-600 to-pink-500 bg-clip-text text-transparent">
            🔥 蛋生动画
          </h1>
          <p className="text-xl text-gray-600">
            AI 驱动的动漫风格视频生成器 — 输入热点，生成萌宠视频！
          </p>
        </motion.div>

        {/* Scene Mode Selector */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-6"
        >
          <h3 className="text-sm font-semibold text-gray-500 mb-3 uppercase tracking-wider">
            选择场景模式
          </h3>
          <div className="grid grid-cols-3 gap-3">
            {SCENES.map((scene) => {
              const Icon = scene.icon;
              return (
                <button
                  key={scene.id}
                  onClick={() => setSceneMode(scene.id as SceneMode)}
                  className={`p-4 rounded-2xl text-center transition-all ${
                    sceneMode === scene.id
                      ? 'bg-purple-600 text-white shadow-lg scale-105'
                      : 'bg-white text-gray-600 hover:bg-purple-50 shadow'
                  }`}
                >
                  <Icon size={24} className="mx-auto mb-1" />
                  <div className="font-semibold text-sm">{scene.name}</div>
                  <div className="text-xs mt-1 opacity-75">{scene.desc}</div>
                </button>
              );
            })}
          </div>
        </motion.div>

        {/* Source Input */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.15 }}
          className="bg-white rounded-2xl shadow-xl p-6 mb-6"
        >
          {/* Input Tabs */}
          <div className="flex gap-2 mb-4 flex-wrap">
            {INPUT_TABS.map(({ type, icon: Icon, label }) => (
              <button
                key={type}
                onClick={() => setSourceType(type)}
                className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm transition-all ${
                  sourceType === type
                    ? 'bg-purple-600 text-white shadow-md'
                    : 'bg-gray-100 text-gray-600 hover:bg-purple-100'
                }`}
              >
                <Icon size={16} />
                {label}
              </button>
            ))}
          </div>

          <textarea
            value={source}
            onChange={(e) => setSource(e.target.value)}
            placeholder={getPlaceholder(sourceType, sceneMode)}
            className="w-full h-32 p-4 border border-gray-200 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-purple-400 text-base"
          />
        </motion.div>

        <AnimatePresence>
          {/* Character Selection (hidden in news mode) */}
          {sceneMode !== 'news' && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="bg-white rounded-2xl shadow-xl p-6 mb-6 overflow-hidden"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">选择角色</h3>
                {sceneMode === 'dialogue' && (
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-gray-500">角色数:</span>
                    {[1, 2, 3].map((n) => (
                      <button
                        key={n}
                        onClick={() => setCharacterCount(n)}
                        className={`w-8 h-8 rounded-full text-sm font-bold transition-all ${
                          characterCount === n
                            ? 'bg-purple-600 text-white'
                            : 'bg-gray-100 text-gray-500 hover:bg-purple-100'
                        }`}
                      >
                        {n}
                      </button>
                    ))}
                  </div>
                )}
              </div>
              <div className="grid grid-cols-4 sm:grid-cols-5 gap-3">
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
            </motion.div>
          )}

          {/* News mode hint */}
          {sceneMode === 'news' && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-gradient-to-r from-amber-50 to-orange-50 rounded-2xl p-5 mb-6 border border-amber-200"
            >
              <div className="flex items-start gap-3">
                <Newspaper size={24} className="text-amber-600 mt-1 flex-shrink-0" />
                <div>
                  <h4 className="font-semibold text-amber-800 mb-1">📰 新闻播报模式</h4>
                  <p className="text-sm text-amber-700">
                    AI 会根据新闻的严肃程度自动匹配动物主播：<br />
                    🟢 娱乐八卦 → 🐶 柴犬 &nbsp; 🟡 社会民生 → 🦉 猫头鹰<br />
                    🟠 财经科技 → 🐧 企鹅 &nbsp; 🔴 重大事件 → 🦁 雄狮
                  </p>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Style Selector (dialogue mode) */}
        {sceneMode === 'dialogue' && (
          <div className="bg-white rounded-2xl shadow-xl p-4 mb-6">
            <h3 className="text-sm font-semibold text-gray-500 mb-2">风格</h3>
            <div className="flex gap-2 flex-wrap">
              {[
                { id: 'auto', label: '🤖 自动' },
                { id: 'funny', label: '😂 搞笑' },
                { id: 'serious', label: '🎯 严肃' },
                { id: 'cute', label: '💕 可爱' },
              ].map((s) => (
                <button
                  key={s.id}
                  onClick={() => setStyle(s.id)}
                  className={`px-4 py-2 rounded-full text-sm transition-all ${
                    style === s.id
                      ? 'bg-purple-600 text-white shadow-md'
                      : 'bg-gray-100 text-gray-600 hover:bg-purple-100'
                  }`}
                >
                  {s.label}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Submit Button */}
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

        {/* Progress Bar */}
        {loading && (
          <div className="mt-6 bg-white rounded-2xl shadow-xl p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-600">{statusText}</span>
              <span className="text-sm font-medium text-purple-600">{progress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <motion.div
                className="h-3 rounded-full bg-gradient-to-r from-purple-500 to-pink-500"
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.5 }}
              />
            </div>
          </div>
        )}

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
              className="w-full rounded-xl bg-black"
              poster="/placeholder-thumb.jpg"
            />
            <div className="flex gap-3 mt-4">
              <a
                href={result}
                download
                className="flex-1 flex items-center justify-center gap-2 py-3 bg-green-500 text-white rounded-xl font-semibold hover:bg-green-600 transition-colors"
              >
                <Download size={18} />
                下载视频
              </a>
              <button
                onClick={() => {
                  setResult(null);
                  setSource('');
                  setProgress(0);
                  setStatusText('');
                }}
                className="flex items-center justify-center gap-2 py-3 px-6 bg-gray-100 text-gray-600 rounded-xl font-semibold hover:bg-gray-200 transition-colors"
              >
                <RotateCcw size={18} />
                再来一次
              </button>
            </div>
          </motion.div>
        )}

        {/* Footer */}
        <div className="mt-12 text-center text-sm text-gray-400">
          <p>🔥 蛋生动画 — AI 动漫视频生成器</p>
          <p className="mt-1">支持 iOS · Web · Windows | MIT License</p>
        </div>
      </div>
    </main>
  );
}

function getPlaceholder(type: SourceType, scene: SceneMode): string {
  if (scene === 'news') {
    if (type === 'web_link') return '粘贴新闻链接...\n例如：https://news.example.com/...';
    if (type === 'text') return '输入或粘贴新闻内容...\n例如：今日股市大涨3%，科技板块领涨...';
    return '粘贴新闻相关内容...';
  }
  if (scene === 'dialogue') {
    if (type === 'douyin_video') return '粘贴抖音对话视频链接...\n例如：https://v.douyin.com/xxxxx';
    if (type === 'text') return '输入对话内容...\n例如：\n甲：今天天气真好！\n乙：是啊，我们去野餐吧！';
    return '粘贴对话相关内容...';
  }
  // auto mode
  if (type === 'text') return '输入你想改编的内容...\n支持文字、链接、视频URL';
  if (type === 'web_link') return '粘贴网页链接...';
  if (type === 'douyin_video') return '粘贴抖音视频链接...';
  return '上传或粘贴内容...';
}
