'use client';

import { useState } from 'react';
import type { SceneMode, SourceType } from '../components/types';
import { STATUS_LABELS } from '../components/constants';

export function useAnimation() {
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

  const getStatusLabel = (status: string): string => {
    return STATUS_LABELS[status] || status;
  };

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

  const handleReset = () => {
    setResult(null);
    setSource('');
    setProgress(0);
    setStatusText('');
  };

  return {
    sceneMode,
    source,
    sourceType,
    character,
    characterCount,
    style,
    loading,
    progress,
    statusText,
    result,
    setSceneMode,
    setSource,
    setSourceType,
    setCharacter,
    setCharacterCount,
    setStyle,
    handleSubmit,
    handleReset,
  };
}
