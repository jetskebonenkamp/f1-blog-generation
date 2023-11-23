from transformers import Trainer, TrainingArguments
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from peft import get_peft_model, LoraConfig, TaskType
import pandas as pd
from datasets import Dataset
import os
import json
import torch


class PeftFinetuner:
    def __init__(self, model_name, folder):
        self.mn, self.folder = model_name, folder
        self.device = torch.device('cuda:0')
        self.ml_data, self.ml_blog = 0, 0

    def instruction(self):
        return 'Create an accurate and entertaining live' +\
               ' blog post for an action happening in a' +\
               ' Formula One race based on' +\
               ' the following structured race data: '

    def getFileNames(self):
        io_filenames, all_pairs = os.listdir(self.folder), {}
        for io_fn in io_filenames:
            if 'ipynb' in io_fn: continue
            full_fn = self.folder + io_fn
            with open(full_fn, 'r') as f:
                io_pairs = json.load(f)
                all_pairs[io_fn.split('.')[0]] = io_pairs
        return all_pairs

    def processDataObject(self, d_objs):
        prompt = 'Write a live blog post describing the ' +\
                 'following event in a Formula 1 race: '
        for d_obj in d_objs:
            i = str(d_objs.index(d_obj))
            ag_i, ac_i, ob_i = 'Agent' + i, 'Action' + i, 'Object' + i
            s_items = [list(s.items()) for s in d_obj['subject']][0]
            action = d_obj['action']
            o_items = list(d_obj['object'].items())
            for s in s_items:
                prompt += ag_i + ' | ' + s[0] + ' | ' + s[1] + ' [SEP] '
            prompt += ac_i + ' | ' + action + ' [SEP] '
            for o in o_items:
                for oo in o[1]:
                    prompt += ob_i + ' | ' + o[0] + ' | ' + oo + ' [SEP] '
        return prompt[:-7]

    def getDataset(self):
        all_pairs = self.getFileNames()
        prompts = []
        for filekey in all_pairs:
            io_pairs = all_pairs[filekey]
            for key in list(io_pairs.keys()):
                llm_input = self.processDataObject(io_pairs[key])
                llm_output, tl_blog = key, len(key.split())
                if tl_blog > self.ml_blog: self.ml_blog = tl_blog + 1
                tl_data = len(llm_input.split())
                if tl_data > self.ml_data: self.ml_data = tl_data + 1
                prompt = {'data': llm_input, 'blogs': llm_output}
                prompts.append(prompt)
            # break
        df = pd.DataFrame.from_records(prompts)
        return Dataset.from_pandas(df)

    def defineModel(self, return_type=''):
        model = AutoModelForSeq2SeqLM.from_pretrained(self.mn)
        peft_config = LoraConfig(
            task_type=TaskType.SEQ_2_SEQ_LM, inference_mode=False, r=8,
            lora_alpha=8, lora_dropout=0.1, target_modules=['q_proj', 'v_proj']
        )
        peft_model = get_peft_model(model, peft_config)
        tokenizer = AutoTokenizer.from_pretrained(self.mn)
        tokenizer.pad_token = tokenizer.eos_token
        if tokenizer.pad_token is None:
            tokenizer.add_special_tokens({'pad_token': '[PAD]'})
        if return_type == 'tok': return tokenizer
        return peft_model, tokenizer

    def preprocessData(self, samples):
        tokenizer, inputs = self.defineModel('tok'), [d for d in samples['data']]
        model_inputs = tokenizer(inputs, max_length=self.ml_data,
                                 pad_to_max_length=True)
        with tokenizer.as_target_tokenizer():
            labels = tokenizer(samples['blogs'], max_length=self.ml_blog,
                               pad_to_max_length=True)
        model_inputs['labels'] = labels['input_ids']
        return model_inputs

    def trainingArguments(self):
        return TrainingArguments(
            per_device_train_batch_size=4, num_train_epochs=3, 
            output_dir='./output', remove_unused_columns=False,
            use_cpu=False, log_level='debug', save_steps=10_000
        )

    def getTokenizedDataset(self):
        ds = self.getDataset()
        tok_ds = ds.map(self.preprocessData, batched=True)
        return tok_ds.remove_columns(ds.column_names)

    def finetuneModel(self):
        model, tokenizer = self.defineModel()
        ds = self.getTokenizedDataset()
        tr_args = self.trainingArguments()
        trainer = Trainer(model=model, train_dataset=ds,
                          tokenizer=tokenizer, args=tr_args)
        fn = './FinetunedModels/' + self.mn.replace('/', '_') + '3'
        trainer.train()
        trainer.save_model(fn)


pf = PeftFinetuner('RUCAIBox/mvp-data-to-text',
                   '../LinguisticFeatureExtraction/IOPairs/')
pf.finetuneModel()