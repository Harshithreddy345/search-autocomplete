"""
Trie Data Structure for Search Autocomplete.

Time Complexities:
- Insert:  O(L) where L = length of word
- Search:  O(L) where L = length of prefix
- Delete:  O(L)

Space: O(N * L) where N = number of words, L = average length
"""

import threading
from typing import Optional


class TrieNode:
    """Each node stores children, end-of-word flag, and search frequency."""

    def __init__(self):
        self.children: dict[str, "TrieNode"] = {}
        self.is_end_of_word: bool = False
        self.frequency: int = 0      # how often this word was searched
        self.word: Optional[str] = None  # full word stored at leaf


class Trie:
    def __init__(self):
        self.root = TrieNode()
        self._lock = threading.Lock()  # thread-safe for concurrent requests

    def insert(self, word: str, frequency: int = 1):
        """Insert a word into the Trie. O(L)"""
        word = word.lower().strip()
        if not word:
            return

        with self._lock:
            node = self.root
            for char in word:
                if char not in node.children:
                    node.children[char] = TrieNode()
                node = node.children[char]

            node.is_end_of_word = True
            node.frequency += frequency
            node.word = word

    def search_prefix(self, prefix: str) -> TrieNode | None:
        """Navigate to the node at end of prefix. O(L)"""
        node = self.root
        for char in prefix.lower():
            if char not in node.children:
                return None
            node = node.children[char]
        return node

    def get_suggestions(self, prefix: str, top_k: int = 5) -> list[dict]:
        """
        Get top-k suggestions for a prefix, sorted by frequency.
        O(L + N) where N = number of nodes in subtree
        """
        prefix = prefix.lower().strip()
        results = []

        start_node = self.search_prefix(prefix)
        if not start_node:
            return []

        # DFS to collect all words under this prefix
        self._dfs(start_node, results)

        # Sort by frequency descending, return top k
        results.sort(key=lambda x: x["frequency"], reverse=True)
        return results[:top_k]

    def _dfs(self, node: TrieNode, results: list):
        """Depth-first search to collect all complete words in subtree."""
        if node.is_end_of_word:
            results.append({
                "word": node.word,
                "frequency": node.frequency
            })
        for child in node.children.values():
            self._dfs(child, results)

    def increment_frequency(self, word: str):
        """Increment search frequency of a word (called on each search)."""
        word = word.lower().strip()
        node = self.root
        for char in word:
            if char not in node.children:
                return  # word not in trie
            node = node.children[char]
        if node.is_end_of_word:
            node.frequency += 1

    def delete(self, word: str) -> bool:
        """Delete a word from the Trie. O(L)"""
        word = word.lower().strip()
        with self._lock:
            path = [self.root]
            node = self.root
            for char in word:
                if char not in node.children:
                    return False
                node = node.children[char]
                path.append(node)

            if not node.is_end_of_word:
                return False

            node.is_end_of_word = False
            node.word = None

            # Prune now-dead nodes from the leaf back up to the root,
            # stopping as soon as a node is still needed by another word.
            for i in range(len(word), 0, -1):
                current = path[i]
                if current.is_end_of_word or current.children:
                    break
                del path[i - 1].children[word[i - 1]]

            return True

    def count_words(self) -> int:
        """Count total words in Trie."""
        count = [0]
        self._count_dfs(self.root, count)
        return count[0]

    def _count_dfs(self, node: TrieNode, count: list):
        if node.is_end_of_word:
            count[0] += 1
        for child in node.children.values():
            self._count_dfs(child, count)
