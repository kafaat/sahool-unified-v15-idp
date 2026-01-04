/**
 * Users Controller
 * متحكم المستخدمين
 */

import {
  Controller,
  Get,
  Post,
  Put,
  Delete,
  Body,
  Param,
  Query,
  HttpCode,
  HttpStatus,
  ForbiddenException,
  UseGuards,
} from '@nestjs/common';
import {
  ApiTags,
  ApiOperation,
  ApiResponse,
  ApiParam,
  ApiQuery,
  ApiBearerAuth,
} from '@nestjs/swagger';
import { UsersService } from './users.service';
import { CreateUserDto } from './dto/create-user.dto';
import { UpdateUserDto } from './dto/update-user.dto';
import { CurrentUser } from '@sahool/nestjs-auth/decorators';
import { JwtAuthGuard } from '../auth/jwt-auth.guard';
import { RolesGuard } from '../auth/roles.guard';
import { Roles } from '../auth/roles.decorator';

@ApiTags('Users')
@UseGuards(JwtAuthGuard)
@Controller('users')
export class UsersController {
  constructor(private readonly usersService: UsersService) {}

  /**
   * Validate resource ownership
   * Users can only access their own data unless they are admins
   */
  private validateResourceOwnership(
    currentUser: any,
    resourceUserId: string,
  ): void {
    // Allow admins to access any user
    if (currentUser?.roles?.includes('admin')) {
      return;
    }

    // Check if the authenticated user is accessing their own data
    if (currentUser?.id !== resourceUserId) {
      throw new ForbiddenException(
        'You do not have permission to access this resource',
      );
    }
  }

  @Post()
  @ApiOperation({
    summary: 'Create a new user',
    description: 'إنشاء مستخدم جديد',
  })
  @ApiResponse({
    status: 201,
    description: 'User created successfully',
  })
  @ApiResponse({
    status: 409,
    description: 'User with this email already exists',
  })
  async create(@Body() createUserDto: CreateUserDto) {
    const user = await this.usersService.create(createUserDto);
    // Remove password hash from response
    const { passwordHash, ...userWithoutPassword } = user;
    return {
      success: true,
      data: userWithoutPassword,
      message: 'User created successfully',
    };
  }

  @Get()
  @ApiOperation({
    summary: 'Get all users',
    description: 'الحصول على جميع المستخدمين',
  })
  @ApiQuery({ name: 'tenantId', required: false })
  @ApiQuery({ name: 'role', required: false })
  @ApiQuery({ name: 'status', required: false })
  @ApiQuery({ name: 'skip', required: false, type: Number })
  @ApiQuery({ name: 'take', required: false, type: Number })
  @ApiResponse({
    status: 200,
    description: 'Users retrieved successfully',
  })
  async findAll(
    @Query('tenantId') tenantId?: string,
    @Query('role') role?: string,
    @Query('status') status?: string,
    @Query('skip') skip?: string,
    @Query('take') take?: string,
  ) {
    const users = await this.usersService.findAll({
      tenantId,
      role,
      status,
      skip: skip ? parseInt(skip) : undefined,
      take: take ? parseInt(take) : undefined,
    });

    // Remove password hashes from response
    const usersWithoutPasswords = users.map((user) => {
      const { passwordHash, ...userWithoutPassword } = user;
      return userWithoutPassword;
    });

    return {
      success: true,
      data: usersWithoutPasswords,
      count: usersWithoutPasswords.length,
    };
  }

  @Get(':id')
  @ApiOperation({
    summary: 'Get a user by ID',
    description: 'الحصول على مستخدم بواسطة المعرف',
  })
  @ApiParam({ name: 'id', description: 'User ID' })
  @ApiResponse({
    status: 200,
    description: 'User retrieved successfully',
  })
  @ApiResponse({
    status: 404,
    description: 'User not found',
  })
  @ApiResponse({
    status: 403,
    description: 'Forbidden - You can only access your own data',
  })
  async findOne(@Param('id') id: string, @CurrentUser() currentUser: any) {
    // Validate resource ownership - users can only access their own data (unless admin)
    this.validateResourceOwnership(currentUser, id);

    const user = await this.usersService.findOne(id);
    const { passwordHash, ...userWithoutPassword } = user;
    return {
      success: true,
      data: userWithoutPassword,
    };
  }

  @Get('email/:email')
  @ApiOperation({
    summary: 'Get a user by email',
    description: 'الحصول على مستخدم بواسطة البريد الإلكتروني',
  })
  @ApiParam({ name: 'email', description: 'User email' })
  @ApiResponse({
    status: 200,
    description: 'User retrieved successfully',
  })
  @ApiResponse({
    status: 404,
    description: 'User not found',
  })
  async findByEmail(@Param('email') email: string) {
    const user = await this.usersService.findByEmail(email);
    if (!user) {
      return {
        success: false,
        message: 'User not found',
      };
    }
    const { passwordHash, ...userWithoutPassword } = user;
    return {
      success: true,
      data: userWithoutPassword,
    };
  }

  @Put(':id')
  @ApiOperation({
    summary: 'Update a user',
    description: 'تحديث مستخدم',
  })
  @ApiParam({ name: 'id', description: 'User ID' })
  @ApiResponse({
    status: 200,
    description: 'User updated successfully',
  })
  @ApiResponse({
    status: 404,
    description: 'User not found',
  })
  @ApiResponse({
    status: 403,
    description: 'Forbidden - You can only update your own data',
  })
  async update(
    @Param('id') id: string,
    @Body() updateUserDto: UpdateUserDto,
    @CurrentUser() currentUser: any,
  ) {
    // Validate resource ownership - users can only update their own data (unless admin)
    this.validateResourceOwnership(currentUser, id);

    const user = await this.usersService.update(id, updateUserDto);
    const { passwordHash, ...userWithoutPassword } = user;
    return {
      success: true,
      data: userWithoutPassword,
      message: 'User updated successfully',
    };
  }

  @Delete(':id')
  @HttpCode(HttpStatus.OK)
  @ApiOperation({
    summary: 'Delete a user (soft delete)',
    description: 'حذف مستخدم (حذف ناعم)',
  })
  @ApiParam({ name: 'id', description: 'User ID' })
  @ApiResponse({
    status: 200,
    description: 'User deleted successfully',
  })
  @ApiResponse({
    status: 404,
    description: 'User not found',
  })
  @ApiResponse({
    status: 403,
    description: 'Forbidden - You can only delete your own data',
  })
  async remove(@Param('id') id: string, @CurrentUser() currentUser: any) {
    // Validate resource ownership - users can only delete their own data (unless admin)
    this.validateResourceOwnership(currentUser, id);

    await this.usersService.remove(id);
    return {
      success: true,
      message: 'User deleted successfully',
    };
  }

  @Delete(':id/hard')
  @UseGuards(RolesGuard)
  @Roles('ADMIN')
  @ApiBearerAuth()
  @HttpCode(HttpStatus.OK)
  @ApiOperation({
    summary: 'Permanently delete a user (Admin only)',
    description: 'حذف مستخدم نهائيا (للمشرفين فقط)',
  })
  @ApiParam({ name: 'id', description: 'User ID' })
  @ApiResponse({
    status: 200,
    description: 'User permanently deleted',
  })
  @ApiResponse({
    status: 401,
    description: 'Unauthorized - Missing or invalid token',
  })
  @ApiResponse({
    status: 403,
    description: 'Forbidden - User does not have ADMIN role',
  })
  @ApiResponse({
    status: 404,
    description: 'User not found',
  })
  async hardDelete(@Param('id') id: string) {
    await this.usersService.hardDelete(id);
    return {
      success: true,
      message: 'User permanently deleted',
    };
  }

  @Get('stats/count/:tenantId')
  @ApiOperation({
    summary: 'Get user count by tenant',
    description: 'الحصول على عدد المستخدمين حسب المستأجر',
  })
  @ApiParam({ name: 'tenantId', description: 'Tenant ID' })
  @ApiResponse({
    status: 200,
    description: 'User count retrieved successfully',
  })
  async countByTenant(@Param('tenantId') tenantId: string) {
    const count = await this.usersService.countByTenant(tenantId);
    return {
      success: true,
      data: { count },
    };
  }

  @Get('stats/active')
  @ApiOperation({
    summary: 'Get active users count',
    description: 'الحصول على عدد المستخدمين النشطين',
  })
  @ApiResponse({
    status: 200,
    description: 'Active users count retrieved successfully',
  })
  async countActive() {
    const count = await this.usersService.countActive();
    return {
      success: true,
      data: { count },
    };
  }
}
