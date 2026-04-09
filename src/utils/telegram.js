/**
 * Telegram API Helper Functions
 */

export async function sendTelegramMessage(token, chatId, text, options = {}) {
  try {
    console.log('Sending message to chat:', chatId);
    
    const url = `https://api.telegram.org/bot${token}/sendMessage`;
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: chatId,
        text: text,
        parse_mode: 'HTML',
        ...options
      })
    });
    
    const result = await response.json();
    
    if (!result.ok) {
      console.error('Telegram API error:', result);
    }
    
    return result;
  } catch (error) {
    console.error('sendTelegramMessage error:', error);
    throw error;
  }
}

export async function sendTelegramPhoto(token, chatId, photoUrl, caption) {
  try {
    console.log('Sending photo to chat:', chatId);
    
    const url = `https://api.telegram.org/bot${token}/sendPhoto`;
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: chatId,
        photo: photoUrl,
        caption: caption,
        parse_mode: 'HTML'
      })
    });
    
    const result = await response.json();
    
    if (!result.ok) {
      console.error('Telegram photo API error:', result);
      // Fallback to text message if photo fails
      await sendTelegramMessage(token, chatId, caption);
    }
    
    return result;
  } catch (error) {
    console.error('sendTelegramPhoto error:', error);
    // Fallback to text message
    await sendTelegramMessage(token, chatId, caption);
  }
}

export async function editTelegramMessage(token, chatId, messageId, text) {
  try {
    const url = `https://api.telegram.org/bot${token}/editMessageText`;
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: chatId,
        message_id: messageId,
        text: text,
        parse_mode: 'HTML'
      })
    });
    
    const result = await response.json();
    return result;
  } catch (error) {
    console.error('editTelegramMessage error:', error);
    throw error;
  }
}

export async function deleteTelegramMessage(token, chatId, messageId) {
  try {
    const url = `https://api.telegram.org/bot${token}/deleteMessage`;
    await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: chatId,
        message_id: messageId
      })
    });
  } catch (error) {
    console.error('deleteTelegramMessage error:', error);
  }
}

export async function answerCallbackQuery(token, queryId, text = '') {
  try {
    const url = `https://api.telegram.org/bot${token}/answerCallbackQuery`;
    await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        callback_query_id: queryId,
        text: text
      })
    });
  } catch (error) {
    console.error('answerCallbackQuery error:', error);
  }
}