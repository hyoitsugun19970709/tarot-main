import { View, Button, Text, Textarea } from '@tarojs/components'
import { useState, useEffect } from 'react'

import './index.scss'
import { tarotApi } from '../../api/tarot_bkd'

type Meanings = string[] | string | Record<string, string[]> | undefined

type DrawCard = {
  id?: string
  name?: string
  orientation?: string
  group?: string
  suit?: string
  meanings?: Meanings
  index?: number
}

type DrawPosition = {
  key: string
  name?: string
  description?: string
  card?: DrawCard | null
}

type DrawSpread = {
  id?: string
  name?: string
  description?: string
  positions?: DrawPosition[]
}

type DrawResult = {
  id?: string
  locale?: string
  spread?: DrawSpread
}

const formatMeanings = (meanings: Meanings) => {
  if (!meanings) return '暂无含义'

  if (Array.isArray(meanings)) {
    return meanings.length ? meanings.join('；') : '暂无含义'
  }

  if (typeof meanings === 'string') {
    return meanings
  }

  const parts = Object.entries(meanings)
    .filter(([, value]) => Array.isArray(value) && value.length > 0)
    .map(([key, value]) => `${key}: ${value.join('；')}`)

  return parts.length ? parts.join(' | ') : '暂无含义'
}

export default function Index() {
  // 用户问题
  const [question, setQuestion] = useState('')

  // AI 推荐牌阵
  const [recommendedSpread, setRecommendedSpread] = useState<string | null>(null)
  const [recommendReason, setRecommendReason] = useState<string | null>(null)

  // 当前结果
  const [result, setResult] = useState<DrawResult | null>(null)

  // AI 解读
  const [interpretation, setInterpretation] = useState<string | null>(null)

  // 加载状态
  const [isRecommending, setIsRecommending] = useState(false)
  const [isDrawing, setIsDrawing] = useState(false)
  const [isInterpreting, setIsInterpreting] = useState(false)

  // 重置
  const reset = () => {
    setRecommendedSpread(null)
    setRecommendReason(null)
    setResult(null)
    setInterpretation(null)
  }

  // AI 推荐牌阵
  const handleRecommend = async () => {
    if (!question.trim()) return

    try {
      setIsRecommending(true)
      const res = await tarotApi.recommend({ question })
      setRecommendedSpread(res.spread)
      setRecommendReason(res.reason)
    } catch (err) {
      console.error(err)
      // 推荐失败时默认三张牌
      setRecommendedSpread('three_card_spread')
      setRecommendReason('使用三张牌阵进行快速解读')
    } finally {
      setIsRecommending(false)
    }
  }

  // 抽牌 + AI 解读
  const handleDraw = async () => {
    if (!question.trim() || !recommendedSpread) return

    try {
      setIsDrawing(true)
      setInterpretation(null)

      const res = await tarotApi.draw({
        name: recommendedSpread,
        arcana: "full",
        orientation: "random"
      })

      setResult(res)

      // 抽牌完成后，调 AI 解读
      if (res.spread) {
        setIsInterpreting(true)
        try {
          const interpretRes = await tarotApi.interpret(question, res.spread)
          setInterpretation(interpretRes.interpretation)
        } catch (err) {
          console.error('解读失败:', err)
          setInterpretation('解读服务暂时不可用，请稍后重试。')
        } finally {
          setIsInterpreting(false)
        }
      }
    } catch (err) {
      console.error(err)
    } finally {
      setIsDrawing(false)
    }
  }

  return (
    <View className='page'>
      {/* 问题输入 */}
      <View className='section'>
        <Text className='label'>你的问题：</Text>
        <Textarea
          className='question-input'
          placeholder='例如：我该不该辞职？'
          value={question}
          onInput={(e) => setQuestion(e.detail.value)}
          maxlength={200}
          disabled={!!recommendedSpread}
        />
      </View>

      {/* 推荐牌阵区域 */}
      {!recommendedSpread ? (
        <>
          <Button
            className='recommend-button'
            onClick={handleRecommend}
            disabled={!question.trim() || isRecommending}
          >
            <Text>{isRecommending ? 'AI分析中...' : '✨ AI 推荐牌阵'}</Text>
          </Button>
        </>
      ) : (
        <>
          <View className='section recommendation-box'>
            <Text className='label'>✨ AI 推荐：</Text>
            <Text className='spread-name'>{recommendedSpread === 'celtic_cross' ? '凯尔特十字（10张牌）' : '三张牌阵'}</Text>
            <Text className='recommend-reason'>{recommendReason}</Text>
          </View>

          <View className='button-row'>
            <Button className='change-button' onClick={reset}>
              <Text>换个问题</Text>
            </Button>
            <Button
              className='draw-button'
              onClick={handleDraw}
              disabled={isDrawing || isInterpreting}
            >
              <Text>{isDrawing ? '抽牌中...' : isInterpreting ? '解读中...' : '✨ 开始抽牌'}</Text>
            </Button>
          </View>
        </>
      )}

      {/* AI 解读 */}
      {interpretation && (
        <View className='section interpretation-box'>
          <Text className='label'>✨ AI 解读：</Text>
          <Text className='interpretation-text'>{interpretation}</Text>
        </View>
      )}

      {/* 结果展示 */}
      {result && (
        <View className='section result-box'>
          <Text className='label'>抽牌结果：</Text>
          <View className='result-line'>
            <Text>
              牌阵：{result.spread?.name || recommendedSpread || '未知牌阵'}
            </Text>
          </View>

          {result.spread?.positions?.length ? (
            <View>
              {result.spread.positions.map((pos, index) => (
                <View key={pos.key || `${index}`} className='position-item'>
                  <Text className='position-title'>
                    位置 {index + 1}：{pos.name || pos.key}
                  </Text>
                  {!!pos.description && (
                    <Text className='result-line'>位置含义：{pos.description}</Text>
                  )}

                  {pos.card ? (
                    <View>
                      <Text className='result-line'>
                        卡牌：{pos.card.name || pos.card.id || '未知卡牌'}
                        {pos.card.orientation === 'reversed' ? ' 🔃' : ' ⬆️'}
                      </Text>
                      <Text className='result-line'>
                        卡牌含义：{formatMeanings(pos.card.meanings)}
                      </Text>
                    </View>
                  ) : (
                    <Text className='result-line'>此位置未抽到卡牌</Text>
                  )}
                </View>
              ))}
            </View>
          ) : (
            <Text className='result-line'>暂无位置数据</Text>
          )}
        </View>
      )}
    </View>
  )
}