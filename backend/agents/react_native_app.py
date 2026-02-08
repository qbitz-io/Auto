import React, { useState } from 'react';
import { View, Text, TextInput, Button, Modal, StyleSheet } from 'react-native';

const ChatInterface = ({ apiKey, instanceUrl }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [approvalVisible, setApprovalVisible] = useState(false);
  const [pendingMessage, setPendingMessage] = useState(null);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const newMessage = { text: input, fromUser: true };
    setMessages([...messages, newMessage]);

    // Show approval popup
    setPendingMessage(input);
    setApprovalVisible(true);
    setInput('');
  };

  const approveMessage = async () => {
    setApprovalVisible(false);
    // Send message to backend API
    try {
      const response = await fetch(`${instanceUrl}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${apiKey}`,
        },
        body: JSON.stringify({ message: pendingMessage }),
      });
      const data = await response.json();
      setMessages([...messages, { text: data.reply, fromUser: false }]);
    } catch (error) {
      setMessages([...messages, { text: 'Error sending message', fromUser: false }]);
    }
    setPendingMessage(null);
  };

  const denyMessage = () => {
    setApprovalVisible(false);
    setPendingMessage(null);
  };

  return (
    <View style={styles.container}>
      <View style={styles.chatWindow}>
        {messages.map((msg, idx) => (
          <Text key={idx} style={msg.fromUser ? styles.userMsg : styles.botMsg}>
            {msg.text}
          </Text>
        ))}
      </View>
      <TextInput
        style={styles.input}
        value={input}
        onChangeText={setInput}
        placeholder="Type your message"
      />
      <Button title="Send" onPress={sendMessage} />

      <Modal visible={approvalVisible} transparent animationType="slide">
        <View style={styles.modalBackground}>
          <View style={styles.modalContent}>
            <Text>Approve sending this message?</Text>
            <Text style={styles.pendingText}>{pendingMessage}</Text>
            <View style={styles.buttonRow}>
              <Button title="Approve" onPress={approveMessage} />
              <Button title="Deny" onPress={denyMessage} color="red" />
            </View>
          </View>
        </View>
      </Modal>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, padding: 10, backgroundColor: '#fff' },
  chatWindow: { flex: 1, marginBottom: 10 },
  userMsg: { alignSelf: 'flex-end', backgroundColor: '#DCF8C6', padding: 8, borderRadius: 5, marginVertical: 2 },
  botMsg: { alignSelf: 'flex-start', backgroundColor: '#ECECEC', padding: 8, borderRadius: 5, marginVertical: 2 },
  input: { borderColor: '#ccc', borderWidth: 1, borderRadius: 5, padding: 8, marginBottom: 10 },
  modalBackground: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: 'rgba(0,0,0,0.5)' },
  modalContent: { backgroundColor: 'white', padding: 20, borderRadius: 10, width: '80%' },
  buttonRow: { flexDirection: 'row', justifyContent: 'space-around', marginTop: 10 },
  pendingText: { marginVertical: 10, fontStyle: 'italic' },
});

export default ChatInterface;
