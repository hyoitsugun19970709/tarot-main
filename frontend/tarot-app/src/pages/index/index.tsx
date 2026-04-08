import { View, Button, Text, Picker } from '@tarojs/components'
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
  // 所有可选牌阵
  const [spreads, setSpreads] = useState<string[]>([])

  // 当前选择
  const [selectedIndex, setSelectedIndex] = useState(0)

  // 当前结果
  const [result, setResult] = useState<DrawResult | null>(null)

  // 初始化：请求 spreads
  useEffect(() => {
    const fetchSpreads = async () => {
      try {
        const res = await tarotApi.spreads()
        // 假设返回：{ spreads: ["a", "b"] }
        setSpreads(res.spreads || [])
      } catch (err) {
        console.error(err)
      }
    }

    fetchSpreads()
  }, [])

  // 抽牌
  const handleDraw = async () => {
    try {
      const selectedSpread = spreads[selectedIndex]

      const res = await tarotApi.draw({
        name: selectedSpread,
        arcana: "full",
        orientation: "random"
      })

      setResult(res)
    } catch (err) {
      console.error(err)
    }
  }

  return (
    <View className='page'>
      {/* 下拉框 */}
      <View className='section'>
        <Text className='label'>选择牌阵：</Text>
        <Picker
          mode="selector"
          range={spreads}
          onChange={(e) => setSelectedIndex(Number(e.detail.value))}
        >
          <View className='picker-value'>
            <Text>
              {spreads.length > 0
                ? spreads[selectedIndex]
                : "加载中..."}
            </Text>
          </View>
        </Picker>
      </View>

      {/* 抽牌按钮 */}
      <Button
        className='draw-button'
        onClick={handleDraw}
        disabled={spreads.length === 0}
      >
        <Text>抽一次塔罗</Text>
      </Button>

      {/* 结果展示 */}
      {result && (
        <View className='section result-box'>
          <Text className='label'>结果：</Text>
          <View className='result-line'>
            <Text>
              牌阵：{result.spread?.name || spreads[selectedIndex] || '未知牌阵'}
            </Text>
          </View>

          {!!result.spread?.description && (
            <View className='result-line'>
              <Text>牌阵说明：{result.spread.description}</Text>
            </View>
          )}

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
                      </Text>
                      <Text className='result-line'>
                        朝向：{pos.card.orientation || '未知'}
                      </Text>
                      <Text className='result-line'>
                        分组：{pos.card.group || '未知'}
                        {pos.card.suit ? ` / 花色：${pos.card.suit}` : ''}
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