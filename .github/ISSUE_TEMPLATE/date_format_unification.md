# 日付フォーマットの統一

## 問題の詳細
## 問題の詳細
現在、`--auto` オプション使用時に、検索クエリの `since` と `until` パラメータで異なる日付フォーマットが使用されています。

- `since`: `YYYY-MM-DD_HH:MM:SS_JST` 形式
- `until`: `YYMMDD_HH:MM:SS_JST` 形式

この不整合により、期待通りの検索結果が得られない可能性があります。

## 再現手順
1. 以下のコマンドを実行:
   ```bash
   python main.py --auto 250805
   ```

2. 出力される検索クエリを確認:
   - 現在: `since:2025-08-05_00:00:00_JST until:250805_23:59:59_JST dtv ビザ`
   - 期待: `since:2025-08-05_00:00:00_JST until:2025-08-05_23:59:59_JST dtv ビザ`

## 期待する動作
`since` と `until` の両方で `YYYY-MM-DD_HH:MM:SS_JST` 形式を使用する

## 関連ファイル
- `src/create_twitter_html_auto.py`
- `main.py`

## タスク
- [ ] `until` パラメータの日付フォーマットを `YYYY-MM-DD_HH:MM:SS_JST` に統一
- [ ] 入力された日付が `YYMMDD` 形式の場合の変換処理を追加
- [ ] テストケースの追加

## 備考
- この修正は後方互換性があります
- 既存の検索クエリの動作に影響はありません
- 他の機能（`--html`, `--extract` オプションなど）の動作にも影響しません
