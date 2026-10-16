import unittest
from app import answer,retrieve,tokens,validate_answer

CHUNKS=[{'id':'a:1:1','source':'a','paragraph':1,'text':'O prazo de reembolso é de 14 dias.'},
        {'id':'b:1:1','source':'b','paragraph':1,'text':'Compras exigem três cotações.'}]

class RetrievalTests(unittest.TestCase):
    def test_accents_are_normalized(self):self.assertIn('cotacoes',tokens('três cotações'))
    def test_correct_document_ranks_first(self):self.assertEqual(retrieve('prazo de reembolso',CHUNKS)[0]['id'],'a:1:1')
    def test_unrelated_question_abstains(self):self.assertTrue(answer('Qual é o salário?',CHUNKS)['abstained'])
    def test_no_model_call_without_retrieval(self):
        # Even a live-provider request must abstain locally when retrieval finds nothing.
        self.assertTrue(answer('salário',CHUNKS,'openai')['abstained'])
    def test_extractive_mode_has_literal_citation(self):
        result=answer('reembolso',CHUNKS)
        self.assertEqual(result['citations'][0]['quote'],CHUNKS[0]['text'])
    def test_fake_source_is_rejected(self):
        value={'answer':'teste','abstained':False,'citations':[{'chunk_id':'fake','quote':'x'}]}
        with self.assertRaises(ValueError):validate_answer(value,CHUNKS)
    def test_nonliteral_quote_is_rejected(self):
        value={'answer':'teste','abstained':False,'citations':[{'chunk_id':'a:1:1','quote':'30 dias'}]}
        with self.assertRaises(ValueError):validate_answer(value,CHUNKS)
    def test_answer_without_citations_is_rejected(self):
        with self.assertRaises(ValueError):validate_answer({'answer':'teste','abstained':False,'citations':[]},CHUNKS)
    def test_abstention_cannot_cite_sources(self):
        with self.assertRaises(ValueError):validate_answer({'answer':'teste','abstained':True,'citations':[{}]},CHUNKS)
    def test_empty_question_is_rejected(self):
        with self.assertRaises(ValueError):answer(' ',CHUNKS)

if __name__=='__main__':unittest.main()
