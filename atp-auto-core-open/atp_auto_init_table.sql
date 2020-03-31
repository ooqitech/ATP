/*
SQLyog  v12.2.6 (64 bit)
MySQL - 5.7.16-log : Database - atp_auto
*********************************************************************
*/


/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
-- CREATE DATABASE /*!32312 IF NOT EXISTS*/`atp_auto` /*!40100 DEFAULT CHARACTER SET utf8 */;

USE `atp_auto`;

SET FOREIGN_KEY_CHECKS=0;

/*Table structure for table `api_celery_task_record` */

DROP TABLE IF EXISTS `api_celery_task_record`;

CREATE TABLE `api_celery_task_record` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `celery_task_no` varchar(36) DEFAULT NULL COMMENT 'celery任务编号',
  `celery_task_status` varchar(10) DEFAULT NULL COMMENT 'celery任务状态',
  `api_run_task_result_id` int(11) DEFAULT NULL COMMENT '关联api_run_task_result.id',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=17465 DEFAULT CHARSET=utf8;

/*Table structure for table `api_company_info` */

DROP TABLE IF EXISTS `api_company_info`;

CREATE TABLE `api_company_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `company_name` varchar(50) NOT NULL COMMENT '公司名称',
  `simple_desc` varchar(100) DEFAULT NULL COMMENT '描述信息',
  `creator` varchar(100) DEFAULT NULL COMMENT '创建人',
  `last_modifier` varchar(100) DEFAULT NULL COMMENT '最近修改人',
  PRIMARY KEY (`id`),
  UNIQUE KEY `company_name` (`company_name`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;

/*Table structure for table `api_env_info` */

DROP TABLE IF EXISTS `api_env_info`;

CREATE TABLE `api_env_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `env_name` varchar(50) NOT NULL COMMENT '环境名称',
  `base_host` varchar(50) DEFAULT NULL COMMENT '基础host地址',
  `dubbo_zookeeper` varchar(50) DEFAULT NULL COMMENT 'zookeeper地址',
  `mq_key` varchar(100) DEFAULT NULL COMMENT 'mq相关配置',
  `db_connect` varchar(200) DEFAULT NULL COMMENT '数据库配置',
  `remote_host` varchar(50) DEFAULT NULL COMMENT '远程服务地址',
  `disconf_host` varchar(50) DEFAULT NULL COMMENT 'disconf地址',
  `redis_connect` varchar(200) DEFAULT NULL COMMENT 'redis地址',
  `simple_desc` varchar(50) DEFAULT NULL COMMENT '描述信息',
  `creator` varchar(100) DEFAULT NULL COMMENT '创建人',
  `last_modifier` varchar(100) DEFAULT NULL COMMENT '最后修改人',
  `server_app_map` varchar(1000) DEFAULT NULL COMMENT '应用服务器ip和应用名MAP',
  `server_default_user` varchar(100) DEFAULT NULL COMMENT '应用服务器默认用户信息',
  PRIMARY KEY (`id`),
  UNIQUE KEY `env_name` (`env_name`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8;

/*Table structure for table `api_generate_data_record` */

DROP TABLE IF EXISTS `api_generate_data_record`;

CREATE TABLE `api_generate_data_record` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `record_date` date DEFAULT NULL COMMENT '记录日期',
  `case_id` varchar(10) DEFAULT NULL COMMENT '用例id',
  `mobile_no` varchar(11) DEFAULT NULL COMMENT '手机号',
  `id_no` varchar(20) DEFAULT NULL COMMENT '身份证号',
  `bank_card_no_credit` varchar(20) DEFAULT NULL COMMENT '信用卡号',
  `bank_card_no_debit` varchar(20) DEFAULT NULL COMMENT '借记卡号',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `api_git_diff_version` */

DROP TABLE IF EXISTS `api_git_diff_version`;

CREATE TABLE `api_git_diff_version` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `api_task_id` int(11) DEFAULT NULL COMMENT '任务id',
  `api_system_id` int(11) DEFAULT NULL COMMENT '工程id',
  `git_branch_name` varchar(100) DEFAULT NULL COMMENT 'git分支名称',
  `old_commit_id` varchar(50) DEFAULT NULL COMMENT '旧commitId',
  `new_commit_id` varchar(50) DEFAULT NULL COMMENT '新commitId',
  `creator` varchar(50) DEFAULT NULL COMMENT '创建人',
  `last_modifier` varchar(50) DEFAULT NULL COMMENT '最近修改人',
  `seq_no` int(11) DEFAULT NULL COMMENT '序列号',
  `detail` text COMMENT '对比详情',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `api_intf_default_request` */

DROP TABLE IF EXISTS `api_intf_default_request`;

CREATE TABLE `api_intf_default_request` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `api_intf_id` int(11) NOT NULL COMMENT '接口id',
  `request` text COMMENT '接口默认请求报文',
  `request_detail` text COMMENT '接口默认请求报文详细信息',
  PRIMARY KEY (`id`),
  UNIQUE KEY `api_intf_id` (`api_intf_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `api_intf_info` */

DROP TABLE IF EXISTS `api_intf_info`;

CREATE TABLE `api_intf_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `intf_name` varchar(500) DEFAULT NULL COMMENT '接口名称',
  `intf_desc` varchar(100) DEFAULT NULL COMMENT '接口中文名',
  `intf_type` varchar(20) DEFAULT NULL COMMENT '接口类型 # HTTP/DUBBO/MQ',
  `intf_info` varchar(1200) DEFAULT NULL COMMENT '接口信息',
  `api_system_id` int(11) DEFAULT NULL COMMENT '工程id',
  `creator` varchar(100) DEFAULT NULL COMMENT '创建人',
  `last_modifier` varchar(100) DEFAULT NULL COMMENT '最近修改人',
  `intf_relation` varchar(200) DEFAULT NULL COMMENT '依赖接口列表',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `api_product_line` */

DROP TABLE IF EXISTS `api_product_line`;

CREATE TABLE `api_product_line` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `product_line_name` varchar(100) NOT NULL COMMENT '产品线节点名称',
  `simple_desc` varchar(100) DEFAULT NULL COMMENT '描述信息',
  `api_company_id` int(11) DEFAULT NULL COMMENT '公司id',
  `creator` varchar(100) DEFAULT NULL COMMENT '创建人',
  `last_modifier` varchar(100) DEFAULT NULL COMMENT '最近修改人',
  `index` int(11) DEFAULT NULL COMMENT '序号',
  `parent_id` int(11) DEFAULT NULL COMMENT '父节点id',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `api_project_info` */

DROP TABLE IF EXISTS `api_project_info`;

CREATE TABLE `api_project_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `project_name` varchar(50) NOT NULL COMMENT '项目名称',
  `simple_desc` varchar(100) DEFAULT NULL COMMENT '描述信息',
  `api_company_id` int(11) DEFAULT NULL COMMENT '公司id',
  `creator` varchar(100) DEFAULT NULL COMMENT '创建人',
  `last_modifier` varchar(100) DEFAULT NULL COMMENT '最近修改人',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `api_project_intf_relation` */

DROP TABLE IF EXISTS `api_project_intf_relation`;

CREATE TABLE `api_project_intf_relation` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `api_project_id` int(11) NOT NULL COMMENT '项目id',
  `api_intf_id` int(11) NOT NULL COMMENT '接口id',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `api_project_system_relation` */

DROP TABLE IF EXISTS `api_project_system_relation`;

CREATE TABLE `api_project_system_relation` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `api_project_id` int(11) NOT NULL COMMENT '项目id',
  `api_system_id` int(11) NOT NULL COMMENT '工程id',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `api_public_variable_info` */

DROP TABLE IF EXISTS `api_public_variable_info`;

CREATE TABLE `api_public_variable_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `variable_name` varchar(100) CHARACTER SET latin1 COLLATE latin1_general_cs NOT NULL COMMENT '公共变量名称',
  `type` varchar(50) NOT NULL COMMENT '公共变量类型 # constant/db/function/files',
  `value` varchar(1000) NOT NULL COMMENT '公共变量的值',
  `simple_desc` varchar(100) DEFAULT NULL COMMENT '描述信息',
  `api_company_id` int(11) DEFAULT NULL COMMENT '公司id',
  `api_system_id` int(11) DEFAULT NULL COMMENT '工程id',
  `creator` varchar(100) DEFAULT NULL COMMENT '创建人',
  `last_modifier` varchar(100) DEFAULT NULL COMMENT '最近修改人',
  `save_as` varchar(10) DEFAULT NULL COMMENT '保存变量的类型 # str/num/bool/list/dict',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `public_variable_info` */

DROP TABLE IF EXISTS `public_variable_info`;

CREATE TABLE `public_variable_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `create_time` datetime DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  `variable_name` varchar(100) NOT NULL,
  `type` varchar(50) NOT NULL,
  `vaule` varchar(1000) NOT NULL,
  `simple_desc` varchar(100) DEFAULT NULL,
  `creator` varchar(100) DEFAULT NULL,
  `system_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `system_id` (`system_id`),
  CONSTRAINT `public_variable_info_ibfk_1` FOREIGN KEY (`system_id`) REFERENCES `system_info` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


/*Table structure for table `api_run_crontab_result` */

DROP TABLE IF EXISTS `api_run_crontab_result`;

CREATE TABLE `api_run_crontab_result` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `create_time` datetime DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  `run_date` date DEFAULT NULL,
  `start_time` datetime DEFAULT NULL,
  `end_time` datetime DEFAULT NULL,
  `api_system_id` int(11) DEFAULT NULL,
  `total_cases` int(11) DEFAULT NULL,
  `not_run_cases` int(11) DEFAULT NULL,
  `run_cases` int(11) DEFAULT NULL,
  `success_cases` int(11) DEFAULT NULL,
  `fail_cases` int(11) DEFAULT NULL,
  `creator` varchar(50) DEFAULT NULL,
  `report_url` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `api_run_task_result` */

DROP TABLE IF EXISTS `api_run_task_result`;

CREATE TABLE `api_run_task_result` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `api_task_id` int(11) DEFAULT NULL COMMENT '任务id',
  `covered_intf_id_list` varchar(5000) DEFAULT NULL COMMENT '覆盖的接口id列表',
  `uncovered_intf_id_list` varchar(5000) DEFAULT NULL COMMENT '未覆盖的接口id列表',
  `total_cases` int(11) DEFAULT NULL COMMENT '总用例数',
  `not_run_cases` int(11) DEFAULT NULL COMMENT '未运行用例数',
  `run_cases` int(11) DEFAULT NULL COMMENT '运行用例数',
  `success_cases` int(11) DEFAULT NULL COMMENT '成功用例数',
  `fail_cases` int(11) DEFAULT NULL COMMENT '失败用例数',
  `creator` varchar(50) DEFAULT NULL COMMENT '任务触发人',
  `start_time` datetime DEFAULT NULL COMMENT '任务开始时间',
  `end_time` datetime DEFAULT NULL COMMENT '任务结束时间',
  `run_date` date DEFAULT NULL COMMENT '运行日期',
  `run_env_id` int(11) DEFAULT NULL COMMENT '运行环境id',
  `report_url` varchar(100) DEFAULT NULL COMMENT '报告地址（已废弃）',
  `run_main_case_in_parallel` int(11) DEFAULT NULL COMMENT '全链路是否并发运行 0:否 1:是',
  `worker_num` int(11) DEFAULT NULL COMMENT '分配worker数量',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `api_system_info` */

DROP TABLE IF EXISTS `api_system_info`;

CREATE TABLE `api_system_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `system_name` varchar(50) NOT NULL COMMENT '工程名称',
  `simple_desc` varchar(100) DEFAULT NULL COMMENT '描述信息',
  `api_company_id` int(11) DEFAULT NULL COMMENT '公司id',
  `creator` varchar(100) DEFAULT NULL COMMENT '创建人',
  `last_modifier` varchar(100) DEFAULT NULL COMMENT '最近修改人',
  `git_url` varchar(100) DEFAULT NULL COMMENT 'git地址',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `api_task_info` */

DROP TABLE IF EXISTS `api_task_info`;

CREATE TABLE `api_task_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `task_name` varchar(100) NOT NULL COMMENT '任务名称',
  `api_project_id` int(11) DEFAULT NULL COMMENT '项目id',
  `task_type` int(11) DEFAULT NULL COMMENT '任务类型 1:人工指定 2:基于代码变更 3:CI构建触发-冒烟测试 4:CI构建触发-回归测试',
  `case_tree` varchar(5000) DEFAULT NULL COMMENT '任务勾选的用例',
  `env_id` int(11) DEFAULT NULL COMMENT '环境id（已废弃）',
  `creator` varchar(50) DEFAULT NULL COMMENT '创建人',
  `last_modifier` varchar(50) DEFAULT NULL COMMENT '最近修改人',
  `receiver_list` varchar(500) DEFAULT NULL COMMENT '任务结果接收人列表',
  `effect_intf_id_list` varchar(5000) DEFAULT NULL COMMENT '覆盖的接口id列表',
  `task_status` int(11) DEFAULT NULL COMMENT '任务可执行状态 0:不可执行 1:可执行',
  `uncovered_info` varchar(2000) DEFAULT NULL COMMENT '未覆盖的信息',
  `api_company_id` int(11) DEFAULT NULL COMMENT '公司id',
  `related_tag_id_list` varchar(100) DEFAULT NULL COMMENT '关联的用例标签id列表',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `api_test_report` */

DROP TABLE IF EXISTS `api_test_report`;

CREATE TABLE `api_test_report` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `start_at` varchar(50) DEFAULT NULL COMMENT '起始时间',
  `duration` varchar(50) DEFAULT NULL COMMENT '耗时',
  `status` varchar(50) DEFAULT NULL COMMENT '状态',
  `run_type` int(11) DEFAULT NULL COMMENT '运行类型 # 0:调试执行 1:测试计划执行',
  `api_project_id` int(11) DEFAULT NULL COMMENT '项目id',
  `url` varchar(150) DEFAULT NULL COMMENT '报告地址',
  `executor` varchar(100) DEFAULT NULL COMMENT '执行人',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `api_testcase_info` */

DROP TABLE IF EXISTS `api_testcase_info`;

CREATE TABLE `api_testcase_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `testcase_name` varchar(200) NOT NULL COMMENT '接口用例标题',
  `type` int(11) NOT NULL COMMENT '用例类型 # 0:default 1:http 2:dubbo 3:mq',
  `include` varchar(400) DEFAULT NULL COMMENT '包含公共变量信息',
  `simple_desc` varchar(1000) DEFAULT NULL COMMENT '描述信息',
  `case_status` int(11) NOT NULL COMMENT '用例启用状态 # 0:启用中 1:已停用',
  `api_intf_id` int(11) DEFAULT NULL COMMENT '接口id',
  `api_request_id` int(11) DEFAULT NULL COMMENT '请求详细信息id',
  `creator` varchar(100) DEFAULT NULL COMMENT '创建人',
  `last_modifier` varchar(100) DEFAULT NULL COMMENT '最近修改人',
  `last_run` tinyint(1) DEFAULT NULL COMMENT '最近一次运行结果 # 0:成功 1:失败',
  `expect_result` varchar(200) DEFAULT NULL COMMENT '预期结果',
  `index` int(11) DEFAULT NULL COMMENT '序号',
  `setup_case_list` varchar(1000) DEFAULT NULL COMMENT '前置用例列表',
  `last_run_time` datetime DEFAULT NULL COMMENT '最近一次运行时间',
  `last_modify_time` datetime DEFAULT NULL COMMENT '最近一次修改用例时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `api_testcase_main` */

DROP TABLE IF EXISTS `api_testcase_main`;

CREATE TABLE `api_testcase_main` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `testcase_name` varchar(200) NOT NULL COMMENT '主用例标题',
  `simple_desc` varchar(1000) DEFAULT NULL COMMENT '描述信息',
  `case_type` int(11) NOT NULL COMMENT '用例类型 0:单接口基础用例 1:接口流程用例 2:全链路用例',
  `case_status` int(11) NOT NULL COMMENT '用例启用状态 0:启用中 1:已停用',
  `api_intf_id` int(11) DEFAULT NULL COMMENT '接口id 当case_type=0/1',
  `api_product_line_id` int(11) DEFAULT NULL COMMENT '产品线id 当case_type=2',
  `sub_list` varchar(1000) DEFAULT NULL COMMENT '子用例id列表',
  `creator` varchar(100) DEFAULT NULL COMMENT '创建人',
  `last_modifier` varchar(100) DEFAULT NULL COMMENT '最近修改人',
  `last_run` tinyint(1) DEFAULT NULL COMMENT '最近一次运行是否成功 0:成功 1:失败',
  `expect_result` varchar(200) DEFAULT NULL COMMENT '预期结果',
  `index` int(11) DEFAULT NULL COMMENT '序号',
  `setup_flow_list` varchar(100) DEFAULT NULL COMMENT '前置列表（未使用）',
  `main_teardown_hooks` varchar(3000) DEFAULT NULL COMMENT '全链路用例独立后置步骤',
  `last_run_time` datetime DEFAULT NULL COMMENT '最近一次运行时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `api_testcase_main_custom_flow` */

DROP TABLE IF EXISTS `api_testcase_main_custom_flow`;

CREATE TABLE `api_testcase_main_custom_flow` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `flow_name` varchar(100) NOT NULL COMMENT '自定义流名称',
  `testcase_id` int(11) NOT NULL COMMENT '主用例id',
  `start_sub_index` int(11) DEFAULT NULL COMMENT '起始子用例序号（已废弃）',
  `end_sub_index` int(11) DEFAULT NULL COMMENT '结束子用例序号（已废弃）',
  `flow_index_list` varchar(255) DEFAULT NULL COMMENT '序号列表',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `api_testcase_main_tag_relation` */

DROP TABLE IF EXISTS `api_testcase_main_tag_relation`;

CREATE TABLE `api_testcase_main_tag_relation` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `api_testcase_id` int(11) NOT NULL COMMENT '主用例id',
  `tag_id` int(11) NOT NULL COMMENT '标签id',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `api_testcase_request` */

DROP TABLE IF EXISTS `api_testcase_request`;

CREATE TABLE `api_testcase_request` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `api_testcase_id` int(11) NOT NULL COMMENT '接口用例id',
  `request` text COMMENT '请求详细信息',
  PRIMARY KEY (`id`),
  UNIQUE KEY `api_testcase_id` (`api_testcase_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `api_testcase_request_qll` */

DROP TABLE IF EXISTS `api_testcase_request_qll`;

CREATE TABLE `api_testcase_request_qll` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `api_testcase_id` int(11) NOT NULL COMMENT '主用例id',
  `request` text COMMENT '请求详细信息',
  PRIMARY KEY (`id`),
  UNIQUE KEY `api_testcase_id` (`api_testcase_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `api_testcase_reuse_record` */

DROP TABLE IF EXISTS `api_testcase_reuse_record`;

CREATE TABLE `api_testcase_reuse_record` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `record_date` date DEFAULT NULL COMMENT '记录日期',
  `api_testcase_id` int(11) DEFAULT NULL COMMENT '接口用例id',
  `total_times` int(11) DEFAULT NULL COMMENT '总计数',
  `success_times` int(11) DEFAULT NULL COMMENT '成功计数',
  `fail_times` int(11) DEFAULT NULL COMMENT '失败计数',
  `api_testcase_main_id` int(11) DEFAULT NULL COMMENT '全链路用例id',
  `been_setup_testcase_id` int(11) DEFAULT NULL COMMENT '被前置的用例id',
  `is_setup` int(11) DEFAULT NULL COMMENT '是否被前置 0: 否， 1: 是',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `api_testcase_sub` */

DROP TABLE IF EXISTS `api_testcase_sub`;

CREATE TABLE `api_testcase_sub` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `sub_name` varchar(200) NOT NULL COMMENT '子用例标题',
  `request_type` int(11) NOT NULL COMMENT '接口请求类型 0:default 1:http 2:dubbo 3:mq',
  `include` varchar(400) DEFAULT NULL COMMENT '包含的公共变量',
  `simple_desc` varchar(200) DEFAULT NULL COMMENT '描述信息',
  `case_type` int(11) NOT NULL COMMENT '用例类型 0:单接口基础用例 1:接口流程用例 2:全链路用例',
  `api_intf_id` int(11) DEFAULT NULL COMMENT '接口id',
  `api_request_id` int(11) DEFAULT NULL COMMENT '用例请求信息id',
  `creator` varchar(100) DEFAULT NULL COMMENT '创建人',
  `last_modifier` varchar(100) DEFAULT NULL COMMENT '最近修改人',
  `expect_result` varchar(200) DEFAULT NULL COMMENT '预期结果',
  `main_list` varchar(1000) DEFAULT NULL COMMENT '关联的主用例id列表',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `api_testcase_tag` */

DROP TABLE IF EXISTS `api_testcase_tag`;

CREATE TABLE `api_testcase_tag` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `tag_name` varchar(100) NOT NULL COMMENT '标签名称',
  `tag_category` varchar(50) DEFAULT NULL COMMENT '标签类别',
  `is_for_task` int(1) DEFAULT NULL COMMENT '测试任务查询时是否展示 0:否 1:是',
  PRIMARY KEY (`id`),
  UNIQUE KEY `tag_name` (`tag_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `api_testcase_tag_relation` */

DROP TABLE IF EXISTS `api_testcase_tag_relation`;

CREATE TABLE `api_testcase_tag_relation` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `api_testcase_id` int(11) NOT NULL COMMENT '接口用例id',
  `tag_id` int(11) NOT NULL COMMENT '标签id',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `base_job_history` */

DROP TABLE IF EXISTS `base_job_history`;

CREATE TABLE `base_job_history` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `summary` varchar(5000) DEFAULT NULL COMMENT 'job汇总信息',
  `is_success` int(11) DEFAULT NULL COMMENT '是否成功 # 0:失败 1:成功',
  `is_update` int(11) DEFAULT NULL COMMENT '是否更新 # 0:否 1:是',
  `error_msg` varchar(200) DEFAULT NULL COMMENT '错误信息',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `base_module_info` */

DROP TABLE IF EXISTS `base_module_info`;

CREATE TABLE `base_module_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `module_name` varchar(80) NOT NULL COMMENT '业务模块名',
  `system_id` int(11) DEFAULT NULL COMMENT '业务系统id',
  `parent_module_id` int(11) DEFAULT NULL COMMENT '父节点id',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `module_info` */

DROP TABLE IF EXISTS `module_info`;

CREATE TABLE `module_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `create_time` datetime DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  `module_name` varchar(80) NOT NULL,
  `test_user` varchar(50) DEFAULT NULL,
  `simple_desc` varchar(100) DEFAULT NULL,
  `system_id` int(11) DEFAULT NULL,
  `creator` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `system_id` (`system_id`),
  CONSTRAINT `module_info_ibfk_1` FOREIGN KEY (`system_id`) REFERENCES `system_info` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `base_module_info_bak` */

DROP TABLE IF EXISTS `base_module_info_bak`;

CREATE TABLE `base_module_info_bak` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `create_time` datetime DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  `module_name` varchar(80) NOT NULL,
  `system_id` int(11) DEFAULT NULL,
  `parent_module_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `base_project_info` */

DROP TABLE IF EXISTS `base_project_info`;

CREATE TABLE `base_project_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `project_name` varchar(50) NOT NULL COMMENT '业务项目名',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `base_project_info` */

DROP TABLE IF EXISTS `project_info`;

CREATE TABLE `project_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `create_time` datetime DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  `project_name` varchar(50) NOT NULL,
  `simple_desc` varchar(100) DEFAULT NULL,
  `creator` varchar(100) DEFAULT NULL,
  `last_modifier` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `project_name` (`project_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


/*Table structure for table `base_system_info` */

DROP TABLE IF EXISTS `base_system_info`;

CREATE TABLE `base_system_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `system_name` varchar(50) NOT NULL COMMENT '业务系统名',
  `project_id` int(11) DEFAULT NULL COMMENT '业务项目id',
  `base_host` varchar(50) DEFAULT NULL COMMENT '（已废弃）',
  `remote_host` varchar(50) DEFAULT NULL COMMENT '（已废弃）',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `base_testcase_info` */

DROP TABLE IF EXISTS `base_testcase_info`;

CREATE TABLE `base_testcase_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `module_id` int(11) DEFAULT NULL COMMENT '业务模块id',
  `testcase_name` varchar(100) NOT NULL COMMENT '业务用例标题',
  `detail` varchar(5000) DEFAULT NULL COMMENT '业务用例详细',
  `test_type` varchar(100) DEFAULT NULL COMMENT '测试类型 # 功能/',
  `req_num` varchar(100) DEFAULT NULL COMMENT '需求编号',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `base_testcase_info_bak` */

DROP TABLE IF EXISTS `base_testcase_info_bak`;

CREATE TABLE `base_testcase_info_bak` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `create_time` datetime DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  `module_id` int(11) DEFAULT NULL,
  `testcase_name` varchar(100) NOT NULL,
  `detail` varchar(2000) DEFAULT NULL,
  `test_type` varchar(100) DEFAULT NULL,
  `req_num` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `ui_case_page_info`;

CREATE TABLE `ui_case_page_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `create_time` datetime DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  `page_name` varchar(100) NOT NULL,
  `simple_desc` varchar(100) DEFAULT NULL,
  `creator` varchar(100) DEFAULT NULL,
  `system_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `ui_case_page_object_info` */

DROP TABLE IF EXISTS `ui_case_page_object_info`;

CREATE TABLE `ui_case_page_object_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `create_time` datetime DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  `object_name` varchar(100) NOT NULL,
  `object_value` varchar(100) NOT NULL,
  `object_by` varchar(50) NOT NULL,
  `simple_desc` varchar(100) DEFAULT NULL,
  `creator` varchar(100) DEFAULT NULL,
  `page_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `page_id` (`page_id`),
  CONSTRAINT `ui_case_page_object_info_ibfk_1` FOREIGN KEY (`page_id`) REFERENCES `ui_case_page_info` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `ui_module_info` */

DROP TABLE IF EXISTS `ui_module_info`;

CREATE TABLE `ui_module_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `create_time` datetime DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  `module_name` varchar(80) NOT NULL,
  `system_id` int(11) DEFAULT NULL,
  `parent_module_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `ui_project_info` */

DROP TABLE IF EXISTS `ui_project_info`;

CREATE TABLE `ui_project_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `create_time` datetime DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  `project_name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `ui_system_info` */

DROP TABLE IF EXISTS `ui_system_info`;

CREATE TABLE `ui_system_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `create_time` datetime DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  `system_name` varchar(50) NOT NULL,
  `project_id` int(11) DEFAULT NULL,
  `base_host` varchar(50) DEFAULT NULL,
  `system_type` varchar(50) DEFAULT NULL,
  `remote_host` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `system_info` */

DROP TABLE IF EXISTS `system_info`;

CREATE TABLE `system_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `create_time` datetime DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  `system_name` varchar(50) NOT NULL,
  `test_user` varchar(50) DEFAULT NULL,
  `dev_user` varchar(50) DEFAULT NULL,
  `publish_app` varchar(50) DEFAULT NULL,
  `simple_desc` varchar(100) DEFAULT NULL,
  `project_id` int(11) DEFAULT NULL,
  `creator` varchar(100) DEFAULT NULL,
  `index` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `project_id` (`project_id`),
  CONSTRAINT `system_info_ibfk_1` FOREIGN KEY (`project_id`) REFERENCES `project_info` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `ui_testcase_info` */

DROP TABLE IF EXISTS `ui_testcase_info`;

CREATE TABLE `ui_testcase_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `create_time` datetime DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  `module_id` int(11) DEFAULT NULL,
  `testcase_name` varchar(100) NOT NULL,
  `simple_desc` varchar(100) DEFAULT NULL,
  `inlude` varchar(100) DEFAULT NULL,
  `request` varchar(2000) DEFAULT NULL,
  `req_num` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `module_id` (`module_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `user` */

DROP TABLE IF EXISTS `user`;

CREATE TABLE `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `username` varchar(100) NOT NULL COMMENT '用户名',
  `password` varchar(50) NOT NULL COMMENT '密码',
  `nickname` varchar(50) NOT NULL COMMENT '昵称（中文名）',
  `level` int(11) DEFAULT NULL COMMENT '权限等级 # 0:Admin 10:Master 20: Developer 25: LimitDeveloper 30: Reporter(unauthorized Developer) 35: Reporter(unauthorized LimitDeveloper) 99: Guest',
  `user_status` int(11) NOT NULL COMMENT '用户认证状态 # 0:已认证  1:未认证',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `alembic_version` */

DROP TABLE IF EXISTS `alembic_version`;

CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `test_plan` */

DROP TABLE IF EXISTS `test_plan`;

CREATE TABLE `test_plan` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `create_time` datetime DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  `plan_name` varchar(100) NOT NULL,
  `test_tree` varchar(1500) NOT NULL,
  `crontab` varchar(100) DEFAULT NULL,
  `simple_desc` varchar(50) DEFAULT NULL,
  `project_id` int(11) DEFAULT NULL,
  `env_id` int(11) DEFAULT NULL,
  `creator` varchar(100) DEFAULT NULL,
  `last_modifier` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `plan_name` (`plan_name`),
  KEY `env_id` (`env_id`),
  KEY `project_id` (`project_id`),
  CONSTRAINT `test_plan_ibfk_2` FOREIGN KEY (`project_id`) REFERENCES `project_info` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `test_report` */

DROP TABLE IF EXISTS `test_report`;

CREATE TABLE `test_report` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `create_time` datetime DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  `start_at` varchar(50) DEFAULT NULL,
  `duration` varchar(50) DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `run_type` int(11) DEFAULT NULL,
  `report` varchar(100) DEFAULT NULL,
  `project_id` int(11) DEFAULT NULL,
  `url` varchar(150) DEFAULT NULL,
  `executor` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `testcase_info` */

DROP TABLE IF EXISTS `testcase_info`;

CREATE TABLE `testcase_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `create_time` datetime DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  `testcase_name` varchar(100) NOT NULL,
  `type` int(11) NOT NULL,
  `include` varchar(400) DEFAULT NULL,
  `request` text NOT NULL,
  `simple_desc` varchar(100) DEFAULT NULL,
  `case_status` int(11) NOT NULL,
  `testsuite_id` int(11) DEFAULT NULL,
  `module_id` int(11) DEFAULT NULL,
  `system_id` int(11) DEFAULT NULL,
  `creator` varchar(100) DEFAULT NULL,
  `last_modifier` varchar(100) DEFAULT NULL,
  `last_run` tinyint(1) DEFAULT NULL,
  `scene_type` varchar(50) DEFAULT NULL,
  `expect_result` varchar(100) DEFAULT NULL,
  `index` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `module_id` (`module_id`),
  KEY `system_id` (`system_id`),
  KEY `testsuite_id` (`testsuite_id`),
  CONSTRAINT `testcase_info_ibfk_1` FOREIGN KEY (`module_id`) REFERENCES `module_info` (`id`),
  CONSTRAINT `testcase_info_ibfk_2` FOREIGN KEY (`system_id`) REFERENCES `system_info` (`id`),
  CONSTRAINT `testcase_info_ibfk_3` FOREIGN KEY (`testsuite_id`) REFERENCES `testsuite_info` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `testcase_tag_relation` */

DROP TABLE IF EXISTS `testcase_tag_relation`;

CREATE TABLE `testcase_tag_relation` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `testcase_id` int(11) NOT NULL,
  `tag_id` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `testsuite_info` */

DROP TABLE IF EXISTS `testsuite_info`;

CREATE TABLE `testsuite_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `create_time` datetime DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  `testsuite_name` varchar(80) NOT NULL,
  `simple_desc` varchar(100) DEFAULT NULL,
  `intf_type` varchar(20) DEFAULT NULL,
  `intf_info` varchar(1200) DEFAULT NULL,
  `module_id` int(11) DEFAULT NULL,
  `creator` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `module_id` (`module_id`),
  CONSTRAINT `testsuite_info_ibfk_1` FOREIGN KEY (`module_id`) REFERENCES `module_info` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;




/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
