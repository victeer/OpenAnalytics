import axios from 'axios';
import config from '../config';

const exampleService = {
  async getExamples() {
    const response = await axios.get(`${config.API.BASE_URL}/examples`);
    return response.data;
  },

  async getExample(id) {
    const response = await axios.get(`${config.API.BASE_URL}/examples/${id}`);
    return response.data;
  },

  async saveExample(exampleData) {
    const response = await axios.post(`${config.API.BASE_URL}/examples`, exampleData);
    return response.data;
  },

  async updateExample(id, exampleData) {
    const response = await axios.put(`${config.API.BASE_URL}/examples/${id}`, exampleData);
    return response.data;
  },

  async deleteExample(id) {
    const response = await axios.delete(`${config.API.BASE_URL}/examples/${id}`);
    return response.data;
  },

  async listExamples() {
    const response = await axios.get(`${config.API.BASE_URL}/examples`);
    return response.data;
  }
};

export default exampleService; 