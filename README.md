# 东方炸弹人

## 背景故事

一觉醒来，灵梦发现幻想乡已经被炸弹人占领。在击破炸弹人后，炸弹人掉落了炸弹。灵梦把炸弹向敌人扔去，炸弹炸了开来。

为了解决这次异变，灵梦踏上了寻找黑幕的旅途。

使用灵梦躲避子弹、夺取炸弹人的炸弹并击破幕后黑手吧！

## 操作方式

1. 按下「z」开火

2. 按下「方向键」移动

3. 按下「x」放炸弹

## 界面

右边的HUD显示了当前获得的分数，剩余的生命和炸弹

## 开发思路

- 初探游戏的ECS架构：Entity、Component、System相分离。

## 开发难点

- 实现游戏的两个状态。一是游戏开始前的菜单，二是游戏中的状态。

- 实现ECS架构。

- 实现资源的释放。

## 主要功能

- 实现分数计算（子弹命中、击破敌人、擦弹均能获取分数）

- 实现关卡设计。游戏引擎已经完成，可以在此基础上随意设计关卡。

- 实现生命值和炸弹。

- 游戏帧率稳定在60hz。

## 缺点

- 因为开发时间有限（仅有一周时间）。因此系统框架和引擎有大量代码复制粘贴。

- 渲染使用PyQt，性能较低。弹幕量大时会卡顿。

- 没有使用测试的弊端：莫名其妙出现却无从调试的BUG。

- 没有能够实现重新开始游戏的功能。

- Windows 平台可能会有听不到背景音乐等BUG。

- 在设计阶段没能决定好直接使用paint渲染还是使用GraphicsItem渲染，最后混杂在一起。