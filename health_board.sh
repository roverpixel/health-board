#!/bin/bash

# Health Board CLI - Bash Edition

# Default base URL for the API. Can be overridden by setting HEALTH_BOARD_URL environment variable.
BASE_URL="${HEALTH_BOARD_URL:-http://127.0.0.1:5000/api}"
VERBOSE=false

# --- Helper Functions ---

# Function to output messages only if VERBOSE is true
verbose_echo() {
    if [ "$VERBOSE" = true ]; then
        echo "$@"
    fi
}

# Function to URL-encode a string in Bash
# Handles ASCII characters. For UTF-8, behavior depends on shell's locale.
# Alphanumeric and -_.~ are not encoded. Space becomes %20. Other chars become %XX.
url_encode_bash() {
    local string="${1}"
    local strlen=${#string}
    local encoded=""
    local pos c o

    for (( pos=0 ; pos<strlen ; pos++ )); do
       c=${string:$pos:1}
       case "$c" in
          [-_.~a-zA-Z0-9] ) o="${c}" ;;
          * )               printf -v o '%%%02x' "'$c"
       esac
       encoded+="${o}"
    done
    echo "${encoded}"
}

# Function to handle API responses
# Usage: handle_response <curl_exit_code> <http_status_code> <response_body>
handle_response() {
    local curl_exit_code="$1"
    local http_status_code="$2"
    local response_body="$3"
    local is_show_command="${4:-false}"

    if [ "$curl_exit_code" -ne 0 ]; then
        echo "Error: curl command failed with exit code $curl_exit_code." >&2
        echo "Response body (if any):" >&2
        echo "$response_body" >&2
        return 1
    fi

    if [ "$http_status_code" -ge 200 ] && [ "$http_status_code" -lt 300 ]; then
        verbose_echo "Success (HTTP $http_status_code):"

        # For 'show' command, always print the JSON body.
        # For other commands, print JSON body only if VERBOSE is true.
        if [ "$is_show_command" = true ]; then
            if command -v jq &> /dev/null && [[ "$response_body" == *"{"* || "$response_body" == *"["* ]]; then
                echo "$response_body" | jq .
            else
                echo "$response_body"
            fi
        elif [ "$VERBOSE" = true ]; then
             if command -v jq &> /dev/null && [[ "$response_body" == *"{"* || "$response_body" == *"["* ]]; then
                echo "$response_body" | jq .
            else
                echo "$response_body"
            fi
        fi
    else
        # Errors always go to stderr
        echo "Error (HTTP $http_status_code):" >&2
        if command -v jq &> /dev/null && [[ "$response_body" == *"{"* || "$response_body" == *"["* ]]; then
            echo "$response_body" | jq . >&2
        else
            echo "$response_body" >&2
        fi
        return 1
    fi
    return 0
}

# --- API Interaction Functions ---

# GET /api/health
api_get_health() {
    local url="${BASE_URL}/health"
    verbose_echo "Fetching health data from $url..."
    response=$(curl -s -w "%{http_code}" -X GET "$url")
    http_status_code=$(echo "$response" | tail -n1)
    response_body=$(echo "$response" | sed '$d')
    handle_response $? "$http_status_code" "$response_body" true # Pass true for is_show_command
}

# POST /api/checkpoint
api_checkpoint() {
    local url="${BASE_URL}/checkpoint"
    verbose_echo "Requesting data checkpoint at $url..."
    response=$(curl -s -w "%{http_code}" -X POST "$url")
    http_status_code=$(echo "$response" | tail -n1)
    response_body=$(echo "$response" | sed '$d')
    handle_response $? "$http_status_code" "$response_body"
}

# POST /api/restore
api_restore() {
    local url="${BASE_URL}/restore"
    verbose_echo "Requesting data restore from $url..."
    response=$(curl -s -w "%{http_code}" -X POST "$url")
    http_status_code=$(echo "$response" | tail -n1)
    response_body=$(echo "$response" | sed '$d')
    handle_response $? "$http_status_code" "$response_body"
}

# POST /api/categories
# Usage: api_create_category <category_name>
api_create_category() {
    local category_name="$1"
    if [ -z "$category_name" ]; then
        echo "Error: Category name cannot be empty." >&2
        return 1
    fi
    local url="${BASE_URL}/categories"
    local data="{\"category_name\": \"$category_name\"}"
    verbose_echo "Creating category '$category_name' at $url..."
    response=$(curl -s -w "%{http_code}" -X POST -H "Content-Type: application/json" -d "$data" "$url")
    http_status_code=$(echo "$response" | tail -n1)
    response_body=$(echo "$response" | sed '$d')
    handle_response $? "$http_status_code" "$response_body"
}

# DELETE /api/categories/<category_name>
# Usage: api_delete_category <category_name>
api_delete_category() {
    local category_name="$1"
    if [ -z "$category_name" ]; then
        echo "Error: Category name cannot be empty." >&2
        return 1
    fi
    # URL encode category name
    local encoded_category_name=$(url_encode_bash "$category_name")
    local url="${BASE_URL}/categories/${encoded_category_name}"
    verbose_echo "Deleting category '$category_name' from $url..."
    response=$(curl -s -w "%{http_code}" -X DELETE "$url")
    http_status_code=$(echo "$response" | tail -n1)
    response_body=$(echo "$response" | sed '$d')
    handle_response $? "$http_status_code" "$response_body"
}

# POST /api/categories/<category_name>/items
# Usage: api_create_item <category_name> <item_name>
api_create_item() {
    local category_name="$1"
    local item_name="$2"
    if [ -z "$category_name" ] || [ -z "$item_name" ]; then
        echo "Error: Category name and item name cannot be empty." >&2
        return 1
    fi
    local encoded_category_name=$(url_encode_bash "$category_name")
    local url="${BASE_URL}/categories/${encoded_category_name}/items"
    local data="{\"item_name\": \"$item_name\"}"
    verbose_echo "Creating item '$item_name' in category '$category_name' at $url..."
    response=$(curl -s -w "%{http_code}" -X POST -H "Content-Type: application/json" -d "$data" "$url")
    http_status_code=$(echo "$response" | tail -n1)
    response_body=$(echo "$response" | sed '$d')
    handle_response $? "$http_status_code" "$response_body"
}

# DELETE /api/categories/<category_name>/items/<item_name>
# Usage: api_delete_item <category_name> <item_name>
api_delete_item() {
    local category_name="$1"
    local item_name="$2"
    if [ -z "$category_name" ] || [ -z "$item_name" ]; then
        echo "Error: Category name and item name cannot be empty." >&2
        return 1
    fi
    local encoded_category_name=$(url_encode_bash "$category_name")
    local encoded_item_name=$(url_encode_bash "$item_name")
    local url="${BASE_URL}/categories/${encoded_category_name}/items/${encoded_item_name}"
    verbose_echo "Deleting item '$item_name' from category '$category_name' at $url..."
    response=$(curl -s -w "%{http_code}" -X DELETE "$url")
    http_status_code=$(echo "$response" | tail -n1)
    response_body=$(echo "$response" | sed '$d')
    handle_response $? "$http_status_code" "$response_body"
}

# PUT /api/categories/<category_name>/items/<item_name>
# Usage: api_update_item <category_name> <item_name> [--status <status>] [--message <message>] [--url <item_url>]
# This function will create the category and item if they don't exist (upsert behavior).
api_update_item() {
    local category_name="$1"
    local item_name="$2"
    shift 2 # Remove category_name and item_name from arguments

    if [ -z "$category_name" ] || [ -z "$item_name" ]; then
        echo "Error: Category name and item name cannot be empty for update." >&2
        return 1
    fi

    # Upsert: Attempt to create category (silently, ignore if exists)
    local create_cat_url="${BASE_URL}/categories"
    local create_cat_data="{\"category_name\": \"$category_name\"}"
    # We don't directly use handle_response here to keep it silent for successful creations or if it already exists.
    # We only care about actual curl errors or unexpected HTTP codes that aren't "already exists" (400 for category).
    local create_cat_response=$(curl -s -w "%{http_code}" -X POST -H "Content-Type: application/json" -d "$create_cat_data" "$create_cat_url")
    local create_cat_http_status=$(echo "$create_cat_response" | tail -n1)
    if [ $? -ne 0 ]; then
        echo "Error: curl command failed during category creation for update." >&2
        return 1
    elif ! [[ "$create_cat_http_status" -ge 200 && "$create_cat_http_status" -lt 300 || "$create_cat_http_status" -eq 400 ]]; then # 400 if category exists
        echo "Error: Unexpected HTTP status $create_cat_http_status during category creation for update." >&2
        echo "$(echo "$create_cat_response" | sed '$d')" >&2
        return 1
    fi

    # Upsert: Attempt to create item (silently, ignore if exists)
    local encoded_category_name_for_item_creation=$(url_encode_bash "$category_name")
    local create_item_url="${BASE_URL}/categories/${encoded_category_name_for_item_creation}/items"
    local create_item_data="{\"item_name\": \"$item_name\"}"
    # Similar to category creation, we want this to be silent on success/already exists.
    local create_item_response=$(curl -s -w "%{http_code}" -X POST -H "Content-Type: application/json" -d "$create_item_data" "$create_item_url")
    local create_item_http_status=$(echo "$create_item_response" | tail -n1)
     if [ $? -ne 0 ]; then
        echo "Error: curl command failed during item creation for update." >&2
        return 1
    # 200 if item already existed, 201 if newly created. 404 if category itself did not exist (should have been created above, but good to check)
    elif ! [[ "$create_item_http_status" -ge 200 && "$create_item_http_status" -lt 300 ]]; then
        echo "Error: Unexpected HTTP status $create_item_http_status during item creation for update." >&2
        echo "$(echo "$create_item_response" | sed '$d')" >&2
        return 1
    fi

    local status_val=""
    local message_val=""
    local url_val=""
    local payload_items=()

    while [ "$#" -gt 0 ]; do
        case "$1" in
            --status)
                status_val="$2"
                payload_items+=("\"status\": \"$status_val\"")
                shift 2
                ;;
            --message)
                message_val="$2"
                # Escape double quotes in message for JSON
                message_val_escaped=$(echo "$message_val" | sed 's/"/\\"/g')
                payload_items+=("\"message\": \"$message_val_escaped\"")
                shift 2
                ;;
            --url)
                url_val="$2"
                payload_items+=("\"url\": \"$url_val\"")
                shift 2
                ;;
            *)
                echo "Error: Unknown option for update: $1" >&2
                print_usage
                return 1
                ;;
        esac
    done

    if [ ${#payload_items[@]} -eq 0 ]; then
        echo "Error: At least one of --status, --message, or --url must be provided for update." >&2
        return 1
    fi

    local data="{"
    for i in "${!payload_items[@]}"; do
        data+="${payload_items[$i]}"
        if [ "$i" -lt $((${#payload_items[@]} - 1)) ]; then
            data+=","
        fi
    done
    data+="}"

    local encoded_category_name=$(url_encode_bash "$category_name")
    local encoded_item_name=$(url_encode_bash "$item_name")
    local url="${BASE_URL}/categories/${encoded_category_name}/items/${encoded_item_name}"

    verbose_echo "Updating item '$item_name' in category '$category_name' at $url with data: $data"
    response=$(curl -s -w "%{http_code}" -X PUT -H "Content-Type: application/json" -d "$data" "$url")
    http_status_code=$(echo "$response" | tail -n1)
    response_body=$(echo "$response" | sed '$d')
    handle_response $? "$http_status_code" "$response_body"
}


# --- Main Script Logic & Usage ---

print_usage() {
    echo "Usage: $0 [-v|--verbose] <command> [options]"
    echo ""
    echo "Global Options:"
    echo "  -v, --verbose                            Enable verbose output. Errors are always printed to stderr."
    echo ""
    echo "Commands:"
    echo "  show                                       Show the current board data. Always outputs board data."
    echo "                                             Use -v for success messages and other details."
    echo "  save                                       Save (checkpoint) the current board data."
    echo "  restore                                    Restore the board data from the checkpoint."
    echo "  create category <category_name>            Create a new category."
    echo "  create item <category_name> <item_name>    Create a new item in a category."
    echo "  remove category <category_name>            Remove a category."
    echo "  remove item <category_name> <item_name>    Remove an item from a category."
    echo "  update <category_name> <item_name>         Update an item. Creates category/item if they don't exist (upsert)."
    echo "         --status <status>                   New status (e.g., running, down, passing, failing, unknown, up)."
    echo "         --message <message>                 Descriptive message for the item's status."
    echo "         --url <url>                         A URL related to the item for more details."
    echo ""
    echo "Environment Variables:"
    echo "  HEALTH_BOARD_URL: Override the default API base URL (Default: http://127.0.0.1:5000/api)."
    echo ""
    echo "Examples:"
    echo "  $0 show"
    echo "  $0 create category Builds"
    echo "  $0 create item Builds \"Main Build\""
    echo "  $0 update Builds \"Main Build\" --status passing --message \"Build successful\" --url http://jenkins.example.com/build/1"
    echo "  $0 remove item Builds \"Main Build\""
    echo "  $0 remove category Builds"
    echo "  $0 save"
    echo "  $0 restore"
    echo ""
    echo "Note: Category and item names with spaces should be quoted."
    echo "Requires curl. If jq is installed, JSON responses will be pretty-printed."
}

# Parse global options like -v or --verbose first
while [[ "$1" =~ ^- && ! "$1" == "--" ]]; do
    case $1 in
        -v | --verbose)
            VERBOSE=true
            shift
            ;;
        *)
            # Unknown option, could be an error or handled by a command
            break
            ;;
    esac
done

if [ "$#" -eq 0 ]; then
    print_usage
    exit 1
fi

COMMAND="$1"
# Check if COMMAND is empty after parsing options (e.g. only -v was passed)
if [ -z "$COMMAND" ]; then
    print_usage
    exit 1
fi
shift # Remove command from arguments

case "$COMMAND" in
    show)
        api_get_health
        ;;
    save)
        api_checkpoint
        ;;
    restore)
        api_restore
        ;;
    create)
        SUB_COMMAND="$1"
        shift
        case "$SUB_COMMAND" in
            category)
                if [ "$#" -ne 1 ]; then
                    echo "Error: Missing category name for 'create category'." >&2
                    print_usage
                    exit 1
                fi
                api_create_category "$1"
                ;;
            item)
                if [ "$#" -ne 2 ]; then
                    echo "Error: Missing category name or item name for 'create item'." >&2
                    print_usage
                    exit 1
                fi
                api_create_item "$1" "$2"
                ;;
            *)
                echo "Error: Unknown 'create' sub-command: $SUB_COMMAND" >&2
                print_usage
                exit 1
                ;;
        esac
        ;;
    remove)
        SUB_COMMAND="$1"
        shift
        case "$SUB_COMMAND" in
            category)
                if [ "$#" -ne 1 ]; then
                    echo "Error: Missing category name for 'remove category'." >&2
                    print_usage
                    exit 1
                fi
                api_delete_category "$1"
                ;;
            item)
                if [ "$#" -ne 2 ]; then
                    echo "Error: Missing category name or item name for 'remove item'." >&2
                    print_usage
                    exit 1
                fi
                api_delete_item "$1" "$2"
                ;;
            *)
                echo "Error: Unknown 'remove' sub-command: $SUB_COMMAND" >&2
                print_usage
                exit 1
                ;;
        esac
        ;;
    update)
        if [ "$#" -lt 3 ]; then # Needs at least category, item, and one option
            echo "Error: Insufficient arguments for 'update'." >&2
            print_usage
            exit 1
        fi
        api_update_item "$@" # Pass all remaining arguments to the update function
        ;;
    *)
        echo "Error: Unknown command: $COMMAND" >&2
        print_usage
        exit 1
        ;;
esac

exit $?
