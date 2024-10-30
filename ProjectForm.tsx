"use client"
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '../ui/input';
import { Textarea } from '../ui/textarea';

const CreateProjectForm = ({userId} : {userId: string | null}) => {
  console.log(userId)

  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [fileUrl, setFileUrl] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch('/api/projects/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ title, description, fileUrl, userId }),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const newProject = await response.json();
      console.log('Project created successfully:', newProject);

      // Optionally, reset form fields or show success message
      setTitle('');
      setDescription('');
      setFileUrl('');
    } catch (error) {
      console.error('Failed to create project', error);
      // Optionally, show error message to user
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <Input 
        type="text" 
        placeholder="Project Title" 
        value={title} 
        onChange={(e) => setTitle(e.target.value)} 
        required 
      />
      <Textarea 
        placeholder="Project Description" 
        value={description} 
        onChange={(e) => setDescription(e.target.value)} 
      />
      <Input 
        type="url" 
        placeholder="File URL" 
        value={fileUrl} 
        onChange={(e) => setFileUrl(e.target.value)} 
        required 
      />
      <Button type="submit">Create Project</Button>
    </form>
  );
};

export default CreateProjectForm;
