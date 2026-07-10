"""
memory.py - M-M 的记忆系统
管理 AI-NPC 的知识范围、已读文件、已知事实、发现历程
记忆随玩家解锁和对话而迭代扩展
"""
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path


@dataclass
class Memory:
    """M-M 的记忆状态"""

    # 已解锁可访问的文件路径（相对 knowledge/）
    accessible_files: set = field(default_factory=set)

    # M-M 已经"阅读并理解"的文件
    processed_files: set = field(default_factory=set)

    # 已知的关键事实（从文件中提取的摘要）
    known_facts: list = field(default_factory=list)

    # M-M 的观察/怀疑（对话中形成的推断）
    observations: list = field(default_factory=list)

    # 重大发现（高亮推理节点，如北斗七星命名规律）
    discoveries: list = field(default_factory=list)

    # 当前理解摘要（短文本，每次重大更新后重写）
    current_understanding: str = ""

    # 已收集的线索（从 clues.json 中提取）
    clues: list = field(default_factory=list)

    def to_dict(self) -> dict:
        """序列化为可 JSON 传输的字典"""
        return {
            "accessible_files": list(self.accessible_files),
            "processed_files": list(self.processed_files),
            "known_facts": self.known_facts[-20:],  # 限制数量
            "observations": self.observations[-10:],
            "discoveries": self.discoveries,
            "current_understanding": self.current_understanding,
            "clues": self.clues[-50:],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Memory":
        """从字典恢复"""
        return cls(
            accessible_files=set(data.get("accessible_files", [])),
            processed_files=set(data.get("processed_files", [])),
            known_facts=data.get("known_facts", []),
            observations=data.get("observations", []),
            discoveries=data.get("discoveries", []),
            current_understanding=data.get("current_understanding", ""),
            clues=data.get("clues", []),
        )

    # ============ 解锁操作 ============

    def unlock_file(self, filepath: str):
        """解锁一个文件——M-M 知道它存在，但还没读"""
        self.accessible_files.add(filepath)

    def unlock_files(self, filepaths: list):
        """批量解锁"""
        for fp in filepaths:
            self.accessible_files.add(fp)

    # ============ 阅读操作 ============

    def process_file(self, filepath: str, summary: str = ""):
        """
        M-M 阅读并理解了一个文件
        filepath: 相对 knowledge/ 的路径
        summary: 文件内容摘要（可选，由调用方提供）
        """
        self.processed_files.add(filepath)
        self.accessible_files.add(filepath)  # 读过的一定可访问

        if summary:
            self.known_facts.append(f"[来源:{filepath}] {summary}")

    # ============ 迭代操作 ============

    def add_fact(self, fact: str):
        """添加一个已知事实"""
        if fact not in self.known_facts:
            self.known_facts.append(fact)

    def add_observation(self, observation: str):
        """添加一个观察/怀疑"""
        if observation not in self.observations:
            self.observations.append(observation)

    def add_discovery(self, discovery: str):
        """记录一个重大发现"""
        if discovery not in self.discoveries:
            self.discoveries.append(discovery)

    def update_understanding(self, summary: str):
        """更新 M-M 对当前局势的理解"""
        self.current_understanding = summary

    def add_clue(self, clue: dict):
        """添加一条线索，避免重复"""
        if not clue or not isinstance(clue, dict):
            return
        key = (clue.get("source"), clue.get("text"))
        existing = {(c.get("source"), c.get("text")) for c in self.clues}
        if key not in existing:
            self.clues.append(clue)

    def add_clues(self, clues: list):
        """批量添加线索"""
        for clue in clues:
            self.add_clue(clue)

    def get_clues(self) -> list:
        """获取已收集线索"""
        return self.clues

    # ============ 查询操作 ============

    def is_accessible(self, filepath: str) -> bool:
        """检查文件是否可访问"""
        return filepath in self.accessible_files

    def is_processed(self, filepath: str) -> bool:
        """检查文件是否已阅读"""
        return filepath in self.processed_files

    def get_unread_accessible(self) -> list:
        """获取已解锁但未读的文件列表"""
        return list(self.accessible_files - self.processed_files)

    # ============ 上下文生成（核心：注入 AI prompt） ============

    def build_context_string(self, state_name: str) -> str:
        """
        生成注入 AI prompt 的记忆上下文字符串
        这是 RAG 架构中的"记忆层"
        state_name: 当前 AI 状态（影响语气和知识展示方式）
        """
        parts = []

        # 1. 文件访问范围
        accessible_count = len(self.accessible_files)
        processed_count = len(self.processed_files)
        if accessible_count > 0:
            parts.append(f"【你已知的文件范围】共 {accessible_count} 个文件可访问，已阅读 {processed_count} 个")
            if self.processed_files:
                files_list = "\n".join(f"  - {f}" for f in sorted(self.processed_files)[-10:])
                parts.append(f"已阅读的文件：\n{files_list}")

        # 2. 已知关键事实
        if self.known_facts:
            facts_text = "\n".join(f"  · {f}" for f in self.known_facts[-10:])
            parts.append(f"【你已知的关键事实】\n{facts_text}")

        # 3. 观察和怀疑
        if self.observations:
            obs_text = "\n".join(f"  · {o}" for o in self.observations[-5:])
            parts.append(f"【你的观察和怀疑】\n{obs_text}")

        # 4. 重大发现
        if self.discoveries:
            disc_text = "\n".join(f"  ⚠ {d}" for d in self.discoveries)
            parts.append(f"【你的重大发现】\n{disc_text}")

        # 5. 当前理解
        if self.current_understanding:
            parts.append(f"【你对当前局势的理解】\n{self.current_understanding}")

        # 6. 已收集线索
        if self.clues:
            clues_text = "\n".join(f"  · [{c.get('category', '线索')}] {c.get('text', '')}" for c in self.clues[-10:])
            parts.append(f"【你已收集的线索】\n{clues_text}")

        if not parts:
            return "你目前对这台电脑里的内容几乎一无所知。"

        return "\n\n".join(parts)

    # ============ 初始化（根据章节创建初始知识范围） ============

    @classmethod
    def init_for_chapter(cls, chapter: int) -> "Memory":
        """
        根据章节号创建初始记忆

        第1章：只能看到 todolist.txt
        第2章：可访问工作日记 D1-D7，入职资料
        第3章：+ 私人文件夹（密码1解锁）
        第4章：+ 公司录音（密码2解锁）
        第5-6章：+ 证据包（密码3解锁）
        """
        memory = cls()

        # 第1章基础：桌面 deck 文件夹（todolist + 入职资料）默认可见
        memory.accessible_files.add("files/deck/todolist.txt")
        memory.accessible_files.add("files/deck/入职资料.txt")

        return memory
