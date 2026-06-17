# def my_own_encode(self, text: str) -> list[int]:
#         """Encode text into token ids with a greedy longest-match lookup
#                                 over the vocab."""
#         try:
#             token_ids: list[int] = []
#             text = text.replace(" ", "Ġ").replace("\n", "Ċ")
#             i = 0
#             while i < len(text):
#                 found_word = None
#                 lentgh_word = 0
#                 for j in range(len(text), i, -1):
#                     word = text[i:j]
#                     # print(f"Slices: {word}")
#                     if word in self.vocab:
#                         # print(f"Found: ---> {word}")
#                         found_word = self.vocab[word]
#                         lentgh_word = len(word)
#                         break
#                 if found_word is not None:
#                     token_ids.append(found_word)
#                     i += lentgh_word
#                 else:
#                     i += 1
#             # print(f"\nthe prompt is: {small_llm.decode(token_ids)}")
#             return token_ids
#         except Exception as e:
#             print(f"Own encode Error: {e}")
#             return []

#     def my_own_decode(self, list_token: list[int]) -> str:
#         """Decode token ids back into text using the vocab mapping."""
#         try:
#             thislist: list[str] = []
#             for i in list_token:
#                 for key, value in self.vocab.items():
#                     if value == i:
#                         thislist.append(key)
#                         break
#             return ''.join(thislist).replace('Ġ', ' ')
#         except Exception as e:
#             print(f"Own decode Error: {e}")
#             return ""