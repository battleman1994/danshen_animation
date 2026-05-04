// 蛋生动画 — AI 动漫视频生成器（UI Redesign v2）
// 设计系统融合：Lovable 温暖基底 + Figma 渐变活力
// 功能完全不变，仅重构视觉层

'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Sparkles, Upload, Link, Type, Play,
  Newspaper, MessageCircle, Zap, Download, RotateCcw,
} from 'lucide-react';

// ── 角色数据 ──────────────────────────────────────────
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

// ── 场景模式 ──────────────────────────────────────────
const SCENES = [
  { id: 'auto', name: '智能识别', icon: Zap, desc: 'AI 自动选择最佳模式' },
  { id: 'dialogue', name: '对话剧场', icon: MessageCircle, desc: '抖音对话 → 动物演绎' },
  { id: 'news', name: '新闻播报', icon: Newspaper, desc: '热点新闻 → 动物主播' },
];

// ── 输入方式标签 ──────────────────────────────────────
const INPUT_TABS = [
  { type: 'text', icon: Type, label: '文字' },
  { type: 'web_link', icon: Link, label: '链接' },
  { type: 'image', icon: Upload, label: '图片' },
  { type: 'douyin_video', icon: Play, label: '抖音' },
] as const;

type SceneMode = 'auto' | 'dialogue' | 'news';
type SourceType = 'text' | 'web_link' | 'image' | 'douyin_video';

// ── 样式常量（代替行内 Tailwind 拼接，保持可维护性）──
const styles = {
  // 卡片
  card: 'bg-white rounded-2xl border border-[#f0e6d8] shadow-sm p-6',
  // 活跃的 pill tab
  pillActive:
    'flex items-center gap-2 px-5 py-2.5 rounded-full text-sm font-medium text-white shadow-md transition-all',
  // 非活跃 pill tab
  pillInactive:
    'flex items-center gap-2 px-5 py-2.5 rounded-full text-sm font-medium transition-all bg-[#f5efe5] text-[#7a7a7a] hover:bg-[#efe5d5] hover:text-[#5a5a5a]',
  // 主要按钮
  btnPrimary:
    'w-full py-4 px-8 rounded-2xl font-bold text-lg text-white shadow-lg hover:shadow-xl transition-all flex items-center justify-center gap-2 disabled:opacity-40 disabled:cursor-not-allowed',
  // section 标题
  sectionTitle: 'text-sm font-semibold text-[#7a7a7a] mb-3 uppercase tracking-wider',
};

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

  // ── 提交逻辑（完全不变）──
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

  // ── UI 渲染 ──────────────────────────────────────────
  return (
    <main className="min-h-screen" style={{ background: '#fef9f0' }}>
      <div className="max-w-2xl mx-auto px-4 py-8 md:py-12">

        {/* ═══════ Header ═══════ */}
        <motion.div
          initial={{ opacity: 0, y: -24 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-10"
        >
          {/* Logo / 标题 */}
          <h1
            className="text-5xl md:text-6xl font-bold mb-3 tracking-tight"
            style={{
              background: 'linear-gradient(135deg, #ff6b6b 0%, #ffa07a 40%, #a78bfa 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
            }}
          >
            🔥 蛋生动画
          </h1>
          <p className="text-lg text-[#7a7a7a] max-w-lg mx-auto leading-relaxed">
            AI 驱动的动漫风格视频生成器 — 输入热点，生成萌宠视频！
          </p>
        </motion.div>

        {/* ═══════ 场景模式选择 ═══════ */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.08 }}
          className="mb-6"
        >
          <h3 className={styles.sectionTitle}>选择场景模式</h3>
          <div className="grid grid-cols-3 gap-3">
            {SCENES.map((scene) => {
              const Icon = scene.icon;
              const isActive = sceneMode === scene.id;
              return (
                <motion.button
                  key={scene.id}
                  whileHover={{ scale: 1.03 }}
                  whileTap={{ scale: 0.97 }}
                  onClick={() => setSceneMode(scene.id as SceneMode)}
                  className={`relative p-4 rounded-2xl text-center transition-all cursor-pointer ${
                    isActive
                      ? 'text-white shadow-lg'
                      : 'bg-white text-[#5a5a5a] border border-[#f0e6d8] hover:border-[#e0d4c0] shadow-sm'
                  }`}
                  style={
                    isActive
                      ? { background: 'linear-gradient(135deg, #ff6b6b, #ffa07a, #a78bfa)' }
                      : undefined
                  }
                >
                  <Icon size={22} className="mx-auto mb-1.5" />
                  <div className="font-semibold text-sm">{scene.name}</div>
                  <div className={`text-xs mt-1 ${isActive ? 'opacity-85' : 'text-[#a8a8a8]'}`}>
                    {scene.desc}
                  </div>
                </motion.button>
              );
            })}
          </div>
        </motion.div>

        {/* ═══════ 输入区域 ═══════ */}
        <motion.div
          initial={{ opacity: 0, scale: 0.97 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.12 }}
          className="bg-white rounded-2xl border border-[#f0e6d8] shadow-sm p-6 mb-6"
        >
          {/* 输入方式 Tabs — Pill 风格 */}
          <div className="flex gap-2 mb-4 flex-wrap">
            {INPUT_TABS.map(({ type, icon: Icon, label }) => (
              <motion.button
                key={type}
                whileHover={{ scale: sourceType !== type ? 1.04 : 1 }}
                whileTap={{ scale: 0.96 }}
                onClick={() => setSourceType(type)}
                className={
                  sourceType === type ? styles.pillActive : styles.pillInactive
                }
                style={
                  sourceType === type
                    ? { background: 'linear-gradient(135deg, #ff6b6b, #ffa07a)' }
                    : undefined
                }
              >
                <Icon size={16} />
                {label}
              </motion.button>
            ))}
          </div>

          {/* 文本输入框 — 温暖风格 */}
          <textarea
            value={source}
            onChange={(e) => setSource(e.target.value)}
            placeholder={getPlaceholder(sourceType, sceneMode)}
            className="w-full h-32 p-4 bg-[#fef9f0] border border-[#f0e6d8] rounded-xl resize-none
                       focus:outline-none focus:border-[#ffa07a] focus:ring-2 focus:ring-[#ffa07a]/20
                       text-[#2d2d2d] placeholder-[#c0b8a8] text-base transition-all"
          />
        </motion.div>

        <AnimatePresence>
          {/* ═══════ 角色选择（非新闻模式） ═══════ */}
          {sceneMode !== 'news' && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="bg-white rounded-2xl border border-[#f0e6d8] shadow-sm p-6 mb-6 overflow-hidden"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-[#2d2d2d]">🎭 选择角色</h3>
                {sceneMode === 'dialogue' && (
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-[#7a7a7a]">角色数:</span>
                    {[1, 2, 3].map((n) => (
                      <motion.button
                        key={n}
                        whileHover={{ scale: 1.08 }}
                        whileTap={{ scale: 0.92 }}
                        onClick={() => setCharacterCount(n)}
                        className="w-8 h-8 rounded-full text-sm font-bold transition-all"
                        style={
                          characterCount === n
                            ? {
                                background: 'linear-gradient(135deg, #ff6b6b, #ffa07a)',
                                color: 'white',
                                boxShadow: '0 2px 6px rgba(255,107,107,0.3)',
                              }
                            : {
                                background: '#f5efe5',
                                color: '#7a7a7a',
                              }
                        }
                      >
                        {n}
                      </motion.button>
                    ))}
                  </div>
                )}
              </div>

              {/* 角色网格 — 卡片 + 选中态渐变边框 */}
              <div className="grid grid-cols-4 sm:grid-cols-5 gap-3">
                {CHARACTERS.map((char) => {
                  const isSelected = character === char.id;
                  return (
                    <motion.button
                      key={char.id}
                      whileHover={{ scale: 1.06 }}
                      whileTap={{ scale: 0.94 }}
                      onClick={() => setCharacter(char.id)}
                      className="relative p-3 rounded-xl text-center transition-all cursor-pointer"
                      style={
                        isSelected
                          ? {
                              background: 'white',
                              boxShadow:
                                '0 0 0 2px rgba(255,107,107,0.5), 0 0 0 4px rgba(255,107,107,0.1), 0 2px 8px rgba(255,107,107,0.15)',
                            }
                          : {
                              background: '#faf7f0',
                              border: '1px solid #f0e6d8',
                            }
                      }
                    >
                      <div className="text-3xl mb-1">{char.emoji}</div>
                      <div className={`text-xs font-medium ${isSelected ? 'text-[#ff6b6b]' : 'text-[#7a7a7a]'}`}>
                        {char.name}
                      </div>
                    </motion.button>
                  );
                })}
              </div>
            </motion.div>
          )}

          {/* ═══════ 新闻模式提示 ═══════ */}
          {sceneMode === 'news' && (
            <motion.div
              initial={{ opacity: 0, y: -8 }}
              animate={{ opacity: 1, y: 0 }}
              className="relative rounded-2xl p-5 mb-6 border overflow-hidden"
              style={{
                background: 'linear-gradient(135deg, #fff8f0, #fff5ea)',
                borderColor: '#f0d8b8',
              }}
            >
              <div className="flex items-start gap-3 relative z-10">
                <Newspaper size={24} className="text-[#e8985a] mt-1 flex-shrink-0" />
                <div>
                  <h4 className="font-semibold text-[#8b5e34] mb-1">📰 新闻播报模式</h4>
                  <p className="text-sm text-[#a07848]">
                    AI 会根据新闻的严肃程度自动匹配动物主播：<br />
                    🟢 娱乐八卦 → 🐶 柴犬 &nbsp; 🟡 社会民生 → 🦉 猫头鹰<br />
                    🟠 财经科技 → 🐧 企鹅 &nbsp; 🔴 重大事件 → 🦁 雄狮
                  </p>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* ═══════ 风格选择（对话模式） ═══════ */}
        {sceneMode === 'dialogue' && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-2xl border border-[#f0e6d8] shadow-sm p-4 mb-6"
          >
            <h3 className={styles.sectionTitle}>风格</h3>
            <div className="flex gap-2 flex-wrap">
              {[
                { id: 'auto', label: '🤖 自动' },
                { id: 'funny', label: '😂 搞笑' },
                { id: 'serious', label: '🎯 严肃' },
                { id: 'cute', label: '💕 可爱' },
              ].map((s) => (
                <motion.button
                  key={s.id}
                  whileHover={{ scale: 1.04 }}
                  whileTap={{ scale: 0.96 }}
                  onClick={() => setStyle(s.id)}
                  className={
                    style === s.id ? styles.pillActive : styles.pillInactive
                  }
                  style={
                    style === s.id
                      ? { background: 'linear-gradient(135deg, #a78bfa, #7c6df0)' }
                      : undefined
                  }
                >
                  {s.label}
                </motion.button>
              ))}
            </div>
          </motion.div>
        )}

        {/* ═══════ 提交按钮 — 渐变动画 ═══════ */}
        <motion.button
          whileHover={!loading && source.trim() ? { scale: 1.02 } : {}}
          whileTap={!loading && source.trim() ? { scale: 0.98 } : {}}
          onClick={handleSubmit}
          disabled={loading || !source.trim()}
          className={styles.btnPrimary}
          style={{
            background: 'linear-gradient(135deg, #ff6b6b 0%, #ffa07a 50%, #a78bfa 100%)',
            backgroundSize: '200% 200%',
          }}
        >
          {loading ? (
            <>
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ repeat: Infinity, duration: 1, ease: 'linear' }}
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

        {/* ═══════ 进度条 ═══════ */}
        {loading && (
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-6 bg-white rounded-2xl border border-[#f0e6d8] shadow-sm p-6"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-[#7a7a7a]">{statusText}</span>
              <span className="text-sm font-semibold text-[#ff6b6b]">{progress}%</span>
            </div>
            <div className="w-full bg-[#f5efe5] rounded-full h-3 overflow-hidden">
              <motion.div
                className="h-3 rounded-full"
                style={{
                  background: 'linear-gradient(90deg, #ff6b6b, #ffa07a, #a78bfa)',
                }}
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.5, ease: 'easeOut' }}
              />
            </div>
          </motion.div>
        )}

        {/* ═══════ 结果显示 ═══════ */}
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-8 bg-white rounded-2xl border border-[#f0e6d8] shadow-sm p-6"
          >
            <h3 className="text-lg font-semibold text-[#2d2d2d] mb-4">✨ 生成完成！</h3>
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
                className="flex-1 flex items-center justify-center gap-2 py-3 rounded-xl font-semibold text-white transition-all hover:opacity-90"
                style={{ background: 'linear-gradient(135deg, #4ade80, #22c55e)' }}
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
                className="flex items-center justify-center gap-2 py-3 px-6 rounded-xl font-semibold
                           bg-[#f5efe5] text-[#7a7a7a] hover:bg-[#efe5d5] hover:text-[#5a5a5a] transition-all"
              >
                <RotateCcw size={18} />
                再来一次
              </button>
            </div>
          </motion.div>
        )}

        {/* ═══════ Footer ═══════ */}
        <div className="mt-12 text-center text-sm text-[#b8a898]">
          <p>🔥 蛋生动画 — AI 动漫视频生成器</p>
          <p className="mt-1">支持 iOS · Web · Windows | MIT License</p>
        </div>
      </div>
    </main>
  );
}

// ── placeholder 辅助函数（完全不变）──
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
