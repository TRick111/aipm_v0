// ChatGPT会話履歴抽出・ダウンロードスクリプト
(function() {
    'use strict';
    
    // article要素内の追加メッセージを取得する関数（セレクタベース）
    function extractAdditionalMessages(article) {
        const additionalMessages = [];
        
        // 特定の構造を持つ要素からテキストを抽出
        const messageSelectors = [
            // 画像生成などのステータスメッセージ
            '.pb-3 span',
            '.pb-3 button span',
            '.relative.w-full.text-start span',
            '.relative.w-full.text-start button span',
            
            // その他の可能性のある構造
            '.flex.items-center.gap-1 span',
            '.text-token-text-secondary',
            
            // より一般的な構造
            'div[class*="pb-"] span',
            'button[disabled] span'
        ];
        
        messageSelectors.forEach(selector => {
            try {
                const elements = article.querySelectorAll(selector);
                elements.forEach(el => {
                    const text = el.textContent.trim();
                    // 空でない、意味のあるテキストをフィルタリング
                    if (text && 
                        text.length > 2 && 
                        !text.match(/^[⭐️✨🎨📷🖼️]+$/) && // 絵文字のみは除外
                        !additionalMessages.includes(text)) {
                        additionalMessages.push(text);
                    }
                });
            } catch (error) {
                console.warn(`セレクタ "${selector}" の処理でエラー:`, error);
            }
        });
        
        return additionalMessages;
    }
    
    // 会話履歴を抽出する関数
    function extractChatHistory() {
        const conversations = [];
        
        // article要素（各会話ターン）を取得
        const articles = document.querySelectorAll('article[data-testid^="conversation-turn-"]');
        
        articles.forEach((article, index) => {
            try {
                // メッセージの役割（user/assistant）を判定
                const userMessage = article.querySelector('[data-message-author-role="user"]');
                const assistantMessage = article.querySelector('[data-message-author-role="assistant"]');
                
                let role = '';
                let content = '';
                let modelSlug = '';
                
                if (userMessage) {
                    role = 'user';
                    // ユーザーメッセージのテキストを取得
                    const textDiv = userMessage.querySelector('.whitespace-pre-wrap');
                    content = textDiv ? textDiv.textContent.trim() : '';
                    
                } else if (assistantMessage) {
                    role = 'assistant';
                    modelSlug = assistantMessage.getAttribute('data-message-model-slug') || '';
                    
                    // アシスタントメッセージのテキストを取得（マークダウン形式）
                    const markdownDiv = assistantMessage.querySelector('.markdown');
                    if (markdownDiv) {
                        // 段落やその他の要素からテキストを取得
                        const paragraphs = markdownDiv.querySelectorAll('p, pre, code, ul, ol, blockquote, h1, h2, h3, h4, h5, h6');
                        if (paragraphs.length > 0) {
                            const textParts = [];
                            paragraphs.forEach(p => {
                                const text = p.textContent.trim();
                                if (text) {
                                    textParts.push(text);
                                }
                            });
                            content = textParts.join('\n\n');
                        } else {
                            // フォールバック：markdown div全体のテキスト
                            content = markdownDiv.textContent.trim();
                        }
                    }
                    
                    // article全体から追加メッセージを取得（セレクタベース）
                    const additionalMessages = extractAdditionalMessages(article);
                    
                    // 追加メッセージがある場合は追加
                    if (additionalMessages.length > 0) {
                        const additionalContent = additionalMessages.join('\n');
                        content = content ? `${additionalContent}\n\n${content}` : additionalContent;
                    }
                    
                } else {
                    // user/assistantのどちらでもない場合、article全体から情報を取得
                    const additionalMessages = extractAdditionalMessages(article);
                    if (additionalMessages.length > 0) {
                        role = 'system'; // システムメッセージとして扱う
                        content = additionalMessages.join('\n');
                    }
                }
                
                if (role && content) {
                    const conversationItem = {
                        turn: index + 1,
                        role: role,
                        content: content
                    };
                    
                    if (modelSlug) {
                        conversationItem.model = modelSlug;
                    }
                    
                    conversations.push(conversationItem);
                }
            } catch (error) {
                console.warn(`メッセージ ${index + 1} の処理でエラー:`, error);
            }
        });
        
        return conversations;
    }
    
    // JSONファイルとしてダウンロードする関数
    function downloadAsJSON(data, filename) {
        const jsonString = JSON.stringify(data, null, 2);
        const blob = new Blob([jsonString], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
    
    // メイン実行部分
    try {
        console.log('ChatGPT会話履歴の抽出を開始...');
        
        const chatHistory = extractChatHistory();
        
        if (chatHistory.length === 0) {
            console.warn('会話履歴が見つかりませんでした。');
            alert('会話履歴が見つかりませんでした。ページが正しく読み込まれているか確認してください。');
            return;
        }
        
        console.log(`${chatHistory.length}件のメッセージを抽出しました。`);
        console.log('抽出データ:', chatHistory);
        
        // メタデータを追加
        const exportData = {
            exportInfo: {
                exportDate: new Date().toISOString(),
                totalMessages: chatHistory.length,
                exportedBy: 'ChatGPT History Extractor Script'
            },
            conversations: chatHistory
        };
        
        // ファイル名を生成（日時付き）
        const now = new Date();
        const timestamp = now.toISOString().slice(0, 19).replace(/:/g, '-');
        const filename = `chatgpt_history_${timestamp}.json`;
        
        // ダウンロード実行
        downloadAsJSON(exportData, filename);
        
        console.log(`会話履歴を${filename}としてダウンロードしました。`);
        alert(`会話履歴を${filename}としてダウンロードしました。\n${chatHistory.length}件のメッセージが含まれています。`);
        
    } catch (error) {
        console.error('エラーが発生しました:', error);
        alert('エラーが発生しました: ' + error.message);
    }
    
})(); 