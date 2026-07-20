# Music Score Maker Skill

[中文](#中文) · [English](#english)

## 中文

一个遵循开放 [Agent Skills 规范](https://github.com/agentskills/agentskills) 的可移植技能。它可以根据歌曲名、艺术家、录音、链接、音频或音乐构想，研究并生成可演奏的乐谱。

主要能力：

- 生成适合阅读和打印的 PDF 乐谱
- 生成可编辑的 MusicXML 与试听/练习 MIDI
- 为初学者调整音域、八度、谱面密度和翻页
- 正确处理萨克斯等移调乐器的实际音高与记谱音高
- 锁定具体录音版本，并以开头、主歌、过渡、高潮、结尾五个检查点核对旋律
- 校验完整曲式、展开后时长、休止/换气、MIDI 音域与移调，避免“文件能打开但音乐不对”
- 解释电子吹管的 USB MIDI、蓝牙 MIDI、MIDI 文件播放和蓝牙音频差异
- 记录资料来源、改编假设和不确定片段

### 安装

```bash
npx skills add liubon/music-score-maker-skill --skill music-score-maker
```

Codex 也可以使用内置安装器按目录安装：

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo liubon/music-score-maker-skill \
  --path skills/music-score-maker
```

也可以把 `skills/music-score-maker/` 整个复制到智能体支持的 skills 目录。不要只复制 `SKILL.md`，因为生成脚本和参考资料也是技能的一部分。

### 运行条件

- Python 3.10 或更高版本；MusicXML/MIDI 构建脚本只使用标准库
- 研究商业歌曲时需要智能体具备合法的网页或用户提供素材访问能力
- 生成 PDF 需要宿主提供乐谱渲染器，例如 Verovio、MuseScore 或同等工具
- 仓库不附带歌曲录音、商业乐谱或生成后的受版权保护歌曲文件

### 验证

```bash
python3 tests/validate_package.py
```

## English

`music-score-maker` is a portable skill that follows the open [Agent Skills specification](https://github.com/agentskills/agentskills). It researches a named or supplied piece and produces playable, traceable sheet music, with printable PDF as the primary reader-facing format when appropriate.

It supports beginner adaptations, transposing instruments, MusicXML, MIDI, PDF engraving guidance, provenance, and electronic-wind/MIDI capability checks.

Install from GitHub with a compatible skills client:

```bash
npx skills add liubon/music-score-maker-skill --skill music-score-maker
```

The MusicXML and MIDI builders require Python 3.10+ and only use the standard library. PDF output additionally requires a notation renderer supplied by the host environment.

## Repository layout

```text
skills/music-score-maker/   Installable skill
tests/                      Portable smoke tests
.github/workflows/          Continuous validation
```

## License

MIT. See [LICENSE](LICENSE).
