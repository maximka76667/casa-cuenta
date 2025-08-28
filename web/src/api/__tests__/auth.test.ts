import { vi } from 'vitest'
import axios from 'axios'
import { signin, signup } from '../auth'
import { useUserStore } from '../../store/userStore'

vi.mock('axios')
vi.mock('../../store/userStore')

const mockedAxios = vi.mocked(axios)
const mockedUserStore = vi.mocked(useUserStore)

describe('Auth API functions', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockedUserStore.getState.mockReturnValue({
      setUser: vi.fn(),
      setAccessToken: vi.fn()
    })
  })

  describe('signin', () => {
    it('signs in user successfully and updates store', async () => {
      const mockUser = { id: '1', email: 'test@example.com' }
      const mockResponse = {
        data: {
          user: mockUser,
          accessToken: 'test_token'
        }
      }
      mockedAxios.post.mockResolvedValue(mockResponse)

      const result = await signin('test@example.com', 'password123')

      expect(mockedAxios.post).toHaveBeenCalledWith(
        'http://localhost:8000/signin',
        {
          email: 'test@example.com',
          password: 'password123'
        },
        {
          withCredentials: true
        }
      )

      expect(result).toEqual(mockResponse.data)
    })
  })

  describe('signup', () => {
    it('signs up user successfully', async () => {
      const mockResponse = {
        data: {
          user: { id: '1', email: 'test@example.com' }
        }
      }
      mockedAxios.post.mockResolvedValue(mockResponse)

      const result = await signup('test@example.com', 'password123')

      expect(mockedAxios.post).toHaveBeenCalledWith(
        'http://localhost:8000/signup',
        {
          email: 'test@example.com',
          password: 'password123'
        },
        {
          withCredentials: true
        }
      )

      expect(result).toEqual(mockResponse.data)
    })
  })
})
