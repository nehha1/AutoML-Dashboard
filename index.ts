export type CreateUserParams = {
    clerkId: string
    firstName: string
    lastName: string
    username: string
    email: string
    photo: string
  }

  export type UpdateUserParams = {
    firstName: string
    lastName: string
    username: string
    photo: string
  }

  export type CreateProjectParams = {
    title: string,
    description?: string,
    fileUrl: string,
    ownerId: string
  }