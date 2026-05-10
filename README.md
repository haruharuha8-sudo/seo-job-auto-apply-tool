# SEO Job Auto Apply Tool (Phase 5)

## セットアップ方法
- Python 3.10+ を用意
- リポジトリ直下で実行

## 実行方法
```bash
python3 -m src.main
```

## CSV入力ファイルの場所
- `data/input_jobs.csv`

## CSV列定義
必須列:
- `source`
- `title`
- `company`
- `role_category`
- `employment_type`
- `budget_min`
- `budget_max`
- `work_style`
- `description`
- `required_skills`（カンマ区切り）
- `nice_to_have`（カンマ区切り）
- `url`
- `posted_at`

## input_format の切り替え方法
`config/config.json` の `input.input_format` を切り替えます。
- `csv`: `data/input_jobs.csv` を使う（運用推奨）
- `sample_json`: `data/sample_jobs.json` を使う（テスト用）

## 注意事項
- 本ツールは自動応募を行いません。
- 案件判定と応募文下書き作成までを行い、応募実行は人間が手動で実施します。

## テスト実行方法
```bash
python3 -m unittest discover -s tests -v
```
