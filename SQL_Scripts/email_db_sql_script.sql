USE [master]
GO
/****** Object:  Database [emailcampaign]    Script Date: 11/21/2023 8:29:11 PM ******/
CREATE DATABASE [emailcampaign]
 CONTAINMENT = NONE
 ON  PRIMARY 
( NAME = N'emailcampaign', FILENAME = N'D:\rdsdbdata\DATA\emailcampaign.mdf' , SIZE = 8192KB , MAXSIZE = UNLIMITED, FILEGROWTH = 10%)
 LOG ON 
( NAME = N'emailcampaign_log', FILENAME = N'D:\rdsdbdata\DATA\emailcampaign_log.ldf' , SIZE = 1024KB , MAXSIZE = 2048GB , FILEGROWTH = 10%)
GO
ALTER DATABASE [emailcampaign] SET COMPATIBILITY_LEVEL = 140
GO
IF (1 = FULLTEXTSERVICEPROPERTY('IsFullTextInstalled'))
begin
EXEC [emailcampaign].[dbo].[sp_fulltext_database] @action = 'enable'
end
GO
ALTER DATABASE [emailcampaign] SET ANSI_NULL_DEFAULT OFF 
GO
ALTER DATABASE [emailcampaign] SET ANSI_NULLS OFF 
GO
ALTER DATABASE [emailcampaign] SET ANSI_PADDING OFF 
GO
ALTER DATABASE [emailcampaign] SET ANSI_WARNINGS OFF 
GO
ALTER DATABASE [emailcampaign] SET ARITHABORT OFF 
GO
ALTER DATABASE [emailcampaign] SET AUTO_CLOSE OFF 
GO
ALTER DATABASE [emailcampaign] SET AUTO_SHRINK OFF 
GO
ALTER DATABASE [emailcampaign] SET AUTO_UPDATE_STATISTICS ON 
GO
ALTER DATABASE [emailcampaign] SET CURSOR_CLOSE_ON_COMMIT OFF 
GO
ALTER DATABASE [emailcampaign] SET CURSOR_DEFAULT  GLOBAL 
GO
ALTER DATABASE [emailcampaign] SET CONCAT_NULL_YIELDS_NULL OFF 
GO
ALTER DATABASE [emailcampaign] SET NUMERIC_ROUNDABORT OFF 
GO
ALTER DATABASE [emailcampaign] SET QUOTED_IDENTIFIER OFF 
GO
ALTER DATABASE [emailcampaign] SET RECURSIVE_TRIGGERS OFF 
GO
ALTER DATABASE [emailcampaign] SET  DISABLE_BROKER 
GO
ALTER DATABASE [emailcampaign] SET AUTO_UPDATE_STATISTICS_ASYNC OFF 
GO
ALTER DATABASE [emailcampaign] SET DATE_CORRELATION_OPTIMIZATION OFF 
GO
ALTER DATABASE [emailcampaign] SET TRUSTWORTHY OFF 
GO
ALTER DATABASE [emailcampaign] SET ALLOW_SNAPSHOT_ISOLATION OFF 
GO
ALTER DATABASE [emailcampaign] SET PARAMETERIZATION SIMPLE 
GO
ALTER DATABASE [emailcampaign] SET READ_COMMITTED_SNAPSHOT OFF 
GO
ALTER DATABASE [emailcampaign] SET HONOR_BROKER_PRIORITY OFF 
GO
ALTER DATABASE [emailcampaign] SET RECOVERY FULL 
GO
ALTER DATABASE [emailcampaign] SET  MULTI_USER 
GO
ALTER DATABASE [emailcampaign] SET PAGE_VERIFY CHECKSUM  
GO
ALTER DATABASE [emailcampaign] SET DB_CHAINING OFF 
GO
ALTER DATABASE [emailcampaign] SET FILESTREAM( NON_TRANSACTED_ACCESS = OFF ) 
GO
ALTER DATABASE [emailcampaign] SET TARGET_RECOVERY_TIME = 0 SECONDS 
GO
ALTER DATABASE [emailcampaign] SET DELAYED_DURABILITY = DISABLED 
GO
ALTER DATABASE [emailcampaign] SET QUERY_STORE = OFF
GO
USE [emailcampaign]
GO
/****** Object:  User [admin]    Script Date: 11/21/2023 8:29:13 PM ******/
CREATE USER [admin] FOR LOGIN [admin] WITH DEFAULT_SCHEMA=[dbo]
GO
ALTER ROLE [db_owner] ADD MEMBER [admin]
GO
/****** Object:  Table [dbo].[email_history]    Script Date: 11/21/2023 8:29:13 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[email_history](
	[recipient_id] [int] NOT NULL,
	[school] [varchar](50) NULL,
	[contact_email] [varchar](50) NULL,
	[sport] [varchar](50) NULL,
	[date_sent] [datetime] NULL,
	[contact_position] [varchar](50) NULL,
	[email_campaign] [varchar](50) NULL,
 CONSTRAINT [PK_email_history] PRIMARY KEY CLUSTERED 
(
	[recipient_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[thread]    Script Date: 11/21/2023 8:29:13 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[thread](
	[thread_id] [int] IDENTITY(1,1) NOT NULL,
	[recipient_id] [int] NOT NULL,
	[date] [datetime] NULL,
	[from] [varchar](30) NULL,
	[to] [varchar](30) NULL,
	[reply] [varchar](1) NULL,
	[subject] [varchar](150) NULL,
	[first_message] [text] NULL,
	[reply_thread] [text] NULL,
 CONSTRAINT [PK_thread_1] PRIMARY KEY CLUSTERED 
(
	[recipient_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
ALTER TABLE [dbo].[thread]  WITH CHECK ADD  CONSTRAINT [FK_thread_email_history] FOREIGN KEY([recipient_id])
REFERENCES [dbo].[email_history] ([recipient_id])
GO
ALTER TABLE [dbo].[thread] CHECK CONSTRAINT [FK_thread_email_history]
GO
USE [master]
GO
ALTER DATABASE [emailcampaign] SET  READ_WRITE 
GO
